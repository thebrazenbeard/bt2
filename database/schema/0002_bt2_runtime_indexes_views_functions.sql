-- BT2 canonical PostgreSQL runtime indexes, views, and functions
-- Captured from WoWSQL bt2-479e4ad9 on 2026-09-10.
-- Apply after 0001_bt2_runtime_baseline.sql.
-- This is the pre-hardening runtime behavior snapshot.

CREATE UNIQUE INDEX material_profiles_one_child_v1 ON bt2.material_profiles USING btree (project_scope, predecessor_digest) WHERE (accepted AND (predecessor_digest IS NOT NULL));
CREATE UNIQUE INDEX material_profiles_one_genesis_v1 ON bt2.material_profiles USING btree (project_scope) WHERE (accepted AND (predecessor_digest IS NULL));
CREATE UNIQUE INDEX operational_checkpoints_one_root_per_agent ON bt2.operational_checkpoints USING btree (agent_key) WHERE (predecessor_checkpoint_id IS NULL);
CREATE UNIQUE INDEX operational_checkpoints_one_successor ON bt2.operational_checkpoints USING btree (predecessor_checkpoint_id) WHERE (predecessor_checkpoint_id IS NOT NULL);
CREATE INDEX work_queue_ready_idx ON bt2.work_queue USING btree (queue_name, target_agent_key, priority, available_at, created_at) WHERE (state = 'READY'::text);
CREATE UNIQUE INDEX workspace_checkpoints_one_successor ON bt2.workspace_checkpoints USING btree (predecessor_checkpoint_id) WHERE (predecessor_checkpoint_id IS NOT NULL);

CREATE OR REPLACE VIEW bt2.agent_topology_v1 AS
 SELECT u.unit_key,
    u.display_name AS unit_name,
    u.unit_type,
    u.orchestrator_agent_key,
    a.agent_key,
    a.display_name,
    a.numerical_identity,
    a.role_kind,
    a.role_summary,
    a.active
   FROM bt2.agent_units u
     JOIN bt2.agents a ON a.unit_key = u.unit_key
  ORDER BY (CASE u.unit_key WHEN 'build_team'::text THEN 1 WHEN 'masamune'::text THEN 2 ELSE 3 END), a.numerical_identity, a.agent_key;

CREATE OR REPLACE VIEW bt2.runtime_visible_materials_v1 AS
 SELECT m.material_id,
    m.project_scope,
    m.schema_version,
    m.semantic_key,
    m.canonical_digest,
    m.source_digest,
    m.canonical_payload,
    m.created_at,
    r.receipt_id,
    r.profile_digest,
    r.policy_digest
   FROM bt2.materials m
     JOIN bt2.material_receipts r ON r.material_id = m.material_id AND r.project_scope = m.project_scope AND r.schema_version = m.schema_version AND r.semantic_key = m.semantic_key AND r.canonical_digest = m.canonical_digest AND r.source_digest = m.source_digest
     JOIN bt2.material_producer_permits p ON p.permit_id = r.permit_id AND p.project_scope = r.project_scope AND p.producer_principal = r.producer_principal AND p.schema_version = r.schema_version AND p.profile_digest = r.profile_digest AND p.policy_digest = r.policy_digest;

CREATE OR REPLACE FUNCTION bt2.assert_no_duplicate_json_keys_v1(j json)
 RETURNS void
 LANGUAGE plpgsql
 IMMUTABLE
AS $function$
declare v json;
begin
  if json_typeof(j)='object' then
    if exists(select 1 from json_each(j) group by key having count(*)>1) then raise exception 'DUPLICATE_JSON_KEY'; end if;
    for v in select value from json_each(j) loop perform bt2.assert_no_duplicate_json_keys_v1(v); end loop;
  elsif json_typeof(j)='array' then
    for v in select value from json_array_elements(j) loop perform bt2.assert_no_duplicate_json_keys_v1(v); end loop;
  end if;
end
$function$;

CREATE OR REPLACE FUNCTION bt2.material_cut_v1(p_project_scope text)
 RETURNS TABLE(facade_id text, profile_digest text, predecessor_digest text, policy_digest text, exact_members json, material_count bigint)
 LANGUAGE sql
 STABLE
AS $function$
with recursive scoped as materialized (
  select p.project_scope,p.profile_digest,p.predecessor_digest,p.policy_digest from bt2.material_profiles p where p.project_scope=p_project_scope and p.accepted
), stats as (
  select count(*)::int as total,
    count(*) filter(where predecessor_digest is null)::int as genesis_count,
    count(*) filter(where predecessor_digest is not null and predecessor_digest=profile_digest)::int as self_count,
    count(*) filter(where predecessor_digest is not null and not exists(select 1 from scoped parent where parent.profile_digest=scoped.predecessor_digest))::int as orphan_count
  from scoped
), forks as (
  select predecessor_digest from scoped where predecessor_digest is not null group by predecessor_digest having count(*)>1
), genesis as (
  select * from scoped where predecessor_digest is null
), walk as (
  select g.project_scope,g.profile_digest,g.predecessor_digest,g.policy_digest,array[g.profile_digest]::text[] as path from genesis g
  union all
  select c.project_scope,c.profile_digest,c.predecessor_digest,c.policy_digest,w.path||c.profile_digest from walk w join scoped c on c.predecessor_digest=w.profile_digest where not c.profile_digest=any(w.path)
), leaves as (
  select s.* from scoped s where not exists(select 1 from scoped c where c.predecessor_digest=s.profile_digest)
), current_profile as (
  select l.project_scope,l.profile_digest,l.predecessor_digest,l.policy_digest from leaves l cross join stats st
  where st.total>0 and st.genesis_count=1 and st.self_count=0 and st.orphan_count=0 and not exists(select 1 from forks) and (select count(*) from walk)=st.total and (select count(*) from leaves)=1
), members as (
  select m.material_id::text as material_id,m.canonical_digest,m.semantic_key,m.source_digest
  from bt2.runtime_visible_materials_v1 m join current_profile p on p.project_scope=m.project_scope and p.profile_digest=m.profile_digest order by m.material_id
)
select 'BT2_MATERIAL_CUT_V1'::text,p.profile_digest,p.predecessor_digest,p.policy_digest,
  coalesce(json_agg(json_build_array(x.material_id,x.canonical_digest,x.semantic_key,x.source_digest) order by x.material_id) filter(where x.material_id is not null),'[]'::json),
  count(x.material_id)::bigint
from current_profile p left join members x on true
group by p.profile_digest,p.predecessor_digest,p.policy_digest
$function$;

CREATE OR REPLACE FUNCTION bt2.append_material_v1(p_material_id uuid, p_project_scope text, p_producer_principal text, p_schema_version text, p_source_digest text, p_payload_text text)
 RETURNS uuid
 LANGUAGE plpgsql
AS $function$
declare
  v_policy record; v_permit record; v_payload_json json; v_payload jsonb; v_receipt uuid:=gen_random_uuid();
  v_semantic_key text; v_canonical_digest text; v_pre record; v_locked record;
begin
  if lower(current_setting('transaction_isolation'))<>'read committed' then raise exception 'APPEND_REQUIRES_READ_COMMITTED'; end if;
  v_payload_json:=p_payload_text::json;
  perform bt2.assert_no_duplicate_json_keys_v1(v_payload_json);
  v_payload:=v_payload_json::jsonb;
  select * into strict v_policy from bt2.material_schema_policy where schema_version=p_schema_version;
  select * into v_pre from bt2.material_cut_v1(p_project_scope);
  if not found then raise exception 'INVALID_ACCEPTED_PROFILE_LINEAGE'; end if;
  lock table bt2.material_profiles in share mode;
  select * into v_locked from bt2.material_cut_v1(p_project_scope);
  if not found then raise exception 'INVALID_ACCEPTED_PROFILE_LINEAGE_AFTER_LOCK'; end if;
  if v_pre.profile_digest is distinct from v_locked.profile_digest or v_pre.predecessor_digest is distinct from v_locked.predecessor_digest or v_pre.policy_digest is distinct from v_locked.policy_digest or v_pre.exact_members::text is distinct from v_locked.exact_members::text then raise exception 'PROFILE_LINEAGE_CHANGED_DURING_ADMISSION'; end if;
  select * into strict v_permit from bt2.material_producer_permits where project_scope=p_project_scope and producer_principal=p_producer_principal and schema_version=p_schema_version and profile_digest=v_locked.profile_digest and policy_digest=v_locked.policy_digest and invalidated_at is null and valid_from<=clock_timestamp() and valid_until>clock_timestamp() for share;
  if v_policy.semantic_fields<>array['semantic_role','subject_key']::text[] or not(v_payload?'semantic_role' and v_payload?'subject_key') then raise exception 'UNKNOWN_OR_INCOMPLETE_SEMANTIC_PROJECTOR'; end if;
  v_semantic_key:=encode(digest(convert_to(jsonb_build_array(v_payload->'semantic_role',v_payload->'subject_key')::text,'UTF8'),'sha256'),'hex');
  v_canonical_digest:=encode(digest(convert_to(v_payload::text,'UTF8'),'sha256'),'hex');
  insert into bt2.materials(material_id,project_scope,schema_version,semantic_key,canonical_digest,source_digest,canonical_payload) values(p_material_id,p_project_scope,p_schema_version,v_semantic_key,v_canonical_digest,p_source_digest,v_payload);
  insert into bt2.material_receipts(receipt_id,material_id,project_scope,producer_principal,permit_id,profile_digest,policy_digest,schema_version,semantic_key,canonical_digest,source_digest) values(v_receipt,p_material_id,p_project_scope,p_producer_principal,v_permit.permit_id,v_locked.profile_digest,v_locked.policy_digest,p_schema_version,v_semantic_key,v_canonical_digest,p_source_digest);
  return v_receipt;
end
$function$;

CREATE OR REPLACE FUNCTION bt2.enqueue_work(p_queue_name text, p_source_agent_key text, p_target_agent_key text, p_work_kind text, p_payload jsonb, p_priority integer DEFAULT 100, p_available_at timestamp with time zone DEFAULT clock_timestamp())
 RETURNS uuid
 LANGUAGE plpgsql
AS $function$
declare v_id uuid:=gen_random_uuid(); v_digest text;
begin
  if p_queue_name is null or btrim(p_queue_name)='' then raise exception 'INVALID_QUEUE_NAME'; end if;
  if p_work_kind is null or btrim(p_work_kind)='' then raise exception 'INVALID_WORK_KIND'; end if;
  if p_payload is null then raise exception 'INVALID_PAYLOAD'; end if;
  v_digest:=encode(digest(convert_to(p_payload::text,'UTF8'),'sha256'),'hex');
  insert into bt2.work_queue(queue_item_id,queue_name,source_agent_key,target_agent_key,work_kind,payload,payload_digest_sha256,priority,available_at) values(v_id,p_queue_name,p_source_agent_key,p_target_agent_key,p_work_kind,p_payload,v_digest,p_priority,p_available_at);
  return v_id;
end
$function$;

CREATE OR REPLACE FUNCTION bt2.claim_work(p_queue_name text, p_target_agent_key text, p_lease_owner text, p_lease_seconds integer DEFAULT 300, p_qty integer DEFAULT 10)
 RETURNS TABLE(queue_item_id uuid, work_kind text, payload jsonb, payload_digest_sha256 text, priority integer, claim_count integer, lease_token uuid, lease_until timestamp with time zone)
 LANGUAGE plpgsql
AS $function$
begin
  if p_lease_seconds<1 or p_lease_seconds>86400 then raise exception 'INVALID_LEASE_SECONDS'; end if;
  if p_qty<1 or p_qty>100 then raise exception 'INVALID_QTY'; end if;
  if p_lease_owner is null or btrim(p_lease_owner)='' then raise exception 'INVALID_LEASE_OWNER'; end if;
  return query
  with picked as (
    select q.queue_item_id from bt2.work_queue q
    where q.queue_name=p_queue_name and q.target_agent_key is not distinct from p_target_agent_key and q.available_at<=clock_timestamp()
      and (q.state='READY' or (q.state='CLAIMED' and q.lease_until<clock_timestamp()))
    order by q.priority asc,q.created_at asc,q.queue_item_id asc for update skip locked limit p_qty
  ), claimed as (
    update bt2.work_queue q set state='CLAIMED', lease_token=gen_random_uuid(), lease_owner=p_lease_owner,
      lease_until=clock_timestamp()+make_interval(secs=>p_lease_seconds), claim_count=q.claim_count+1, claimed_at=clock_timestamp()
    from picked p where q.queue_item_id=p.queue_item_id
    returning q.queue_item_id,q.work_kind,q.payload,q.payload_digest_sha256,q.priority,q.claim_count,q.lease_token,q.lease_until
  )
  select c.queue_item_id,c.work_kind,c.payload,c.payload_digest_sha256,c.priority,c.claim_count,c.lease_token,c.lease_until from claimed c order by c.priority,c.queue_item_id;
end
$function$;

CREATE OR REPLACE FUNCTION bt2.release_work(p_queue_item_id uuid, p_lease_token uuid, p_error text DEFAULT NULL::text, p_retry_delay_seconds integer DEFAULT 0, p_dead boolean DEFAULT false)
 RETURNS boolean
 LANGUAGE plpgsql
AS $function$
declare v_rows integer;
begin
  if p_retry_delay_seconds<0 or p_retry_delay_seconds>604800 then raise exception 'INVALID_RETRY_DELAY'; end if;
  update bt2.work_queue set state=case when p_dead then 'DEAD' else 'READY' end,
    available_at=case when p_dead then available_at else clock_timestamp()+make_interval(secs=>p_retry_delay_seconds) end,
    lease_token=null,lease_owner=null,lease_until=null,last_error=p_error
  where queue_item_id=p_queue_item_id and state='CLAIMED' and lease_token=p_lease_token;
  get diagnostics v_rows=row_count;
  if v_rows<>1 then raise exception 'STALE_OR_INVALID_LEASE'; end if;
  return true;
end
$function$;

CREATE OR REPLACE FUNCTION bt2.ack_work(p_queue_item_id uuid, p_lease_token uuid)
 RETURNS boolean
 LANGUAGE plpgsql
AS $function$
declare v_rows integer;
begin
  update bt2.work_queue set state='ACKED',acked_at=clock_timestamp(),lease_until=null
  where queue_item_id=p_queue_item_id and state='CLAIMED' and lease_token=p_lease_token and lease_until>=clock_timestamp();
  get diagnostics v_rows=row_count;
  if v_rows<>1 then raise exception 'STALE_OR_INVALID_LEASE'; end if;
  return true;
end
$function$;

CREATE OR REPLACE FUNCTION bt2.report_bug(p_operation_id uuid, p_intake_key text, p_title text, p_description text DEFAULT ''::text, p_severity text DEFAULT 'MEDIUM'::text, p_component text DEFAULT NULL::text, p_reported_by text DEFAULT NULL::text, p_assigned_agent_key text DEFAULT 'one'::text, p_evidence jsonb DEFAULT '{}'::jsonb)
 RETURNS TABLE(out_bug_id uuid, out_event_id uuid, out_queue_item_id uuid, idempotent_replay boolean)
 LANGUAGE plpgsql
AS $function$
declare
  v_key text:=btrim(p_intake_key); v_title text:=btrim(p_title); v_sev text:=upper(btrim(p_severity)); v_agent text:=lower(btrim(p_assigned_agent_key));
  v_request jsonb; v_digest text; v_existing record; v_bug record; v_bug_id uuid:=gen_random_uuid(); v_event_id uuid:=gen_random_uuid(); v_queue_id uuid; v_result jsonb; v_result_digest text;
begin
  perform pg_advisory_xact_lock(hashtextextended(p_operation_id::text,0));
  if v_key is null or v_key='' then raise exception 'INVALID_INTAKE_KEY'; end if;
  if v_title is null or v_title='' then raise exception 'INVALID_TITLE'; end if;
  if v_sev not in ('LOW','MEDIUM','HIGH','CRITICAL') then raise exception 'INVALID_SEVERITY'; end if;
  if not exists(select 1 from bt2.agents a where a.agent_key=v_agent and a.active) then raise exception 'INVALID_TARGET_AGENT'; end if;
  v_request:=jsonb_build_object('kind','REPORT_BUG','intake_key',v_key,'title',v_title,'description',coalesce(p_description,''),'severity',v_sev,'component',p_component,'reported_by',p_reported_by,'assigned_agent_key',v_agent,'evidence',coalesce(p_evidence,'{}'::jsonb));
  v_digest:=encode(digest(convert_to(v_request::text,'UTF8'),'sha256'),'hex');
  select * into v_existing from bt2.operations where operation_id=p_operation_id;
  if found then
    if v_existing.request_digest_sha256<>v_digest then raise exception 'OPERATION_ID_REUSE_CONFLICT'; end if;
    if v_existing.state='VERIFIED' then return query select (v_existing.result_payload->>'bug_id')::uuid,(v_existing.result_payload->>'event_id')::uuid,(v_existing.result_payload->>'queue_item_id')::uuid,true; return; end if;
    raise exception using message='OPERATION_REQUIRES_RECONCILIATION state='||v_existing.state;
  end if;
  insert into bt2.operations(operation_id,actor_agent_key,operation_kind,target_locator,idempotency_key,request_digest_sha256,request_payload,state)
    values(p_operation_id,case when exists(select 1 from bt2.agents where agent_key=lower(coalesce(p_reported_by,''))) then lower(p_reported_by) else null end,'REPORT_BUG','bt2.bugs:intake:'||v_key,v_key,v_digest,v_request,'PREPARED');
  insert into bt2.bugs(bug_id,intake_key,intake_digest_sha256,title,description,severity,status,component,reported_by,assigned_agent_key,state_version,evidence)
    values(v_bug_id,v_key,v_digest,v_title,coalesce(p_description,''),v_sev,'NEW',p_component,p_reported_by,v_agent,1,coalesce(p_evidence,'{}'::jsonb)) on conflict(intake_key) do nothing;
  if not found then
    select * into strict v_bug from bt2.bugs where intake_key=v_key;
    if v_bug.intake_digest_sha256 is distinct from v_digest then raise exception 'INTAKE_KEY_REUSE_CONFLICT'; end if;
    select e.bug_event_id,e.queue_item_id into v_event_id,v_queue_id from bt2.bug_events e where e.bug_id=v_bug.bug_id and e.state_version=1;
    v_bug_id:=v_bug.bug_id;
  else
    insert into bt2.bug_events(bug_event_id,bug_id,state_version,event_type,actor_agent_key,operation_id,details) values(v_event_id,v_bug_id,1,'REPORTED',null,p_operation_id,jsonb_build_object('assigned_agent_key',v_agent));
    v_queue_id:=bt2.enqueue_work('agent_dispatch','one',v_agent,'BUG_REPORTED',jsonb_build_object('bug_id',v_bug_id,'event_id',v_event_id,'state_version',1,'assigned_agent_key',v_agent),10,clock_timestamp());
    update bt2.bug_events set queue_item_id=v_queue_id where bug_event_id=v_event_id;
  end if;
  v_result:=jsonb_build_object('bug_id',v_bug_id,'event_id',v_event_id,'queue_item_id',v_queue_id);
  v_result_digest:=encode(digest(convert_to(v_result::text,'UTF8'),'sha256'),'hex');
  update bt2.operations set state='VERIFIED',resolved_at=clock_timestamp(),result_payload=v_result,result_digest_sha256=v_result_digest,updated_at=clock_timestamp() where operation_id=p_operation_id;
  return query select v_bug_id,v_event_id,v_queue_id,false;
end
$function$;

CREATE OR REPLACE FUNCTION bt2.route_bug(p_operation_id uuid, p_bug_id uuid, p_expected_state_version bigint, p_target_agent_key text, p_actor_agent_key text DEFAULT 'one'::text, p_reason text DEFAULT NULL::text)
 RETURNS TABLE(out_event_id uuid, out_state_version bigint, out_queue_item_id uuid, idempotent_replay boolean)
 LANGUAGE plpgsql
AS $function$
declare
  v_target text:=lower(btrim(p_target_agent_key)); v_actor text:=lower(btrim(p_actor_agent_key)); v_request jsonb; v_digest text; v_existing record; v_bug record; v_event uuid:=gen_random_uuid(); v_state bigint; v_queue uuid; v_result jsonb; v_result_digest text;
begin
  perform pg_advisory_xact_lock(hashtextextended(p_operation_id::text,0));
  if not exists(select 1 from bt2.agents where agent_key=v_target and active) then raise exception 'INVALID_TARGET_AGENT'; end if;
  v_request:=jsonb_build_object('kind','ROUTE_BUG','bug_id',p_bug_id,'expected_state_version',p_expected_state_version,'target_agent_key',v_target,'actor_agent_key',v_actor,'reason',p_reason);
  v_digest:=encode(digest(convert_to(v_request::text,'UTF8'),'sha256'),'hex');
  select * into v_existing from bt2.operations where operation_id=p_operation_id;
  if found then
    if v_existing.request_digest_sha256<>v_digest then raise exception 'OPERATION_ID_REUSE_CONFLICT'; end if;
    if v_existing.state='VERIFIED' then return query select (v_existing.result_payload->>'event_id')::uuid,(v_existing.result_payload->>'state_version')::bigint,(v_existing.result_payload->>'queue_item_id')::uuid,true; return; end if;
    raise exception using message='OPERATION_REQUIRES_RECONCILIATION state='||v_existing.state;
  end if;
  select * into v_bug from bt2.bugs where bug_id=p_bug_id for update;
  if not found then raise exception 'BUG_NOT_FOUND'; end if;
  if v_bug.state_version<>p_expected_state_version then raise exception using message='STALE_STATE_VERSION'; end if;
  if v_bug.status='CLOSED' then raise exception 'BUG_CLOSED'; end if;
  insert into bt2.operations(operation_id,actor_agent_key,operation_kind,target_locator,idempotency_key,request_digest_sha256,request_payload,state) values(p_operation_id,case when exists(select 1 from bt2.agents where agent_key=v_actor) then v_actor else null end,'ROUTE_BUG','bt2.bugs:'||p_bug_id::text,p_operation_id::text,v_digest,v_request,'PREPARED');
  v_state:=v_bug.state_version+1;
  update bt2.bugs set assigned_agent_key=v_target,state_version=v_state,updated_at=clock_timestamp() where bug_id=p_bug_id;
  insert into bt2.bug_events(bug_event_id,bug_id,state_version,event_type,actor_agent_key,operation_id,details) values(v_event,p_bug_id,v_state,'ROUTED',case when exists(select 1 from bt2.agents where agent_key=v_actor) then v_actor else null end,p_operation_id,jsonb_build_object('from_agent_key',v_bug.assigned_agent_key,'to_agent_key',v_target,'reason',p_reason));
  v_queue:=bt2.enqueue_work('agent_dispatch',v_actor,v_target,'BUG_ROUTED',jsonb_build_object('bug_id',p_bug_id,'event_id',v_event,'state_version',v_state,'target_agent_key',v_target),10,clock_timestamp());
  update bt2.bug_events set queue_item_id=v_queue where bug_event_id=v_event;
  v_result:=jsonb_build_object('event_id',v_event,'state_version',v_state,'queue_item_id',v_queue);
  v_result_digest:=encode(digest(convert_to(v_result::text,'UTF8'),'sha256'),'hex');
  update bt2.operations set state='VERIFIED',resolved_at=clock_timestamp(),result_payload=v_result,result_digest_sha256=v_result_digest,updated_at=clock_timestamp() where operation_id=p_operation_id;
  return query select v_event,v_state,v_queue,false;
end
$function$;

CREATE OR REPLACE FUNCTION bt2.update_bug_status(p_operation_id uuid, p_bug_id uuid, p_expected_state_version bigint, p_status text, p_actor_agent_key text DEFAULT 'one'::text, p_note text DEFAULT NULL::text)
 RETURNS TABLE(out_event_id uuid, out_state_version bigint, out_status text, out_queue_item_id uuid, idempotent_replay boolean)
 LANGUAGE plpgsql
AS $function$
declare
  v_requested text:=upper(btrim(p_status)); v_actor text:=lower(btrim(p_actor_agent_key)); v_request jsonb; v_digest text; v_existing record; v_bug record; v_event uuid:=gen_random_uuid(); v_state bigint; v_status text; v_queue uuid; v_result jsonb; v_result_digest text;
begin
  perform pg_advisory_xact_lock(hashtextextended(p_operation_id::text,0));
  if v_requested not in ('NEW','TRIAGED','IN_PROGRESS','BLOCKED','FIXED','VERIFYING','CLOSED','REOPENED') then raise exception 'INVALID_STATUS'; end if;
  v_request:=jsonb_build_object('kind','UPDATE_BUG_STATUS','bug_id',p_bug_id,'expected_state_version',p_expected_state_version,'requested_status',v_requested,'actor_agent_key',v_actor,'note',p_note);
  v_digest:=encode(digest(convert_to(v_request::text,'UTF8'),'sha256'),'hex');
  select * into v_existing from bt2.operations where operation_id=p_operation_id;
  if found then
    if v_existing.request_digest_sha256<>v_digest then raise exception 'OPERATION_ID_REUSE_CONFLICT'; end if;
    if v_existing.state='VERIFIED' then return query select (v_existing.result_payload->>'event_id')::uuid,(v_existing.result_payload->>'state_version')::bigint,v_existing.result_payload->>'status',nullif(v_existing.result_payload->>'queue_item_id','')::uuid,true; return; end if;
    raise exception using message='OPERATION_REQUIRES_RECONCILIATION state='||v_existing.state;
  end if;
  select * into v_bug from bt2.bugs where bug_id=p_bug_id for update;
  if not found then raise exception 'BUG_NOT_FOUND'; end if;
  if v_bug.state_version<>p_expected_state_version then raise exception 'STALE_STATE_VERSION'; end if;
  if v_requested='REOPENED' and v_bug.status<>'CLOSED' then raise exception 'REOPEN_REQUIRES_CLOSED'; end if;
  if v_bug.status='CLOSED' and v_requested<>'REOPENED' then raise exception 'BUG_CLOSED_REQUIRES_REOPEN'; end if;
  insert into bt2.operations(operation_id,actor_agent_key,operation_kind,target_locator,idempotency_key,request_digest_sha256,request_payload,state) values(p_operation_id,case when exists(select 1 from bt2.agents where agent_key=v_actor) then v_actor else null end,'UPDATE_BUG_STATUS','bt2.bugs:'||p_bug_id::text,p_operation_id::text,v_digest,v_request,'PREPARED');
  v_state:=v_bug.state_version+1;
  if v_requested='REOPENED' then
    v_status:='NEW';
    update bt2.bugs set status='NEW',assigned_agent_key='one',state_version=v_state,updated_at=clock_timestamp(),closed_at=null where bug_id=p_bug_id;
    insert into bt2.bug_events(bug_event_id,bug_id,state_version,event_type,actor_agent_key,operation_id,details) values(v_event,p_bug_id,v_state,'REOPENED',case when exists(select 1 from bt2.agents where agent_key=v_actor) then v_actor else null end,p_operation_id,jsonb_build_object('from_status',v_bug.status,'to_status','NEW','note',p_note));
    v_queue:=bt2.enqueue_work('agent_dispatch',v_actor,'one','BUG_REOPENED',jsonb_build_object('bug_id',p_bug_id,'event_id',v_event,'state_version',v_state),10,clock_timestamp());
    update bt2.bug_events set queue_item_id=v_queue where bug_event_id=v_event;
  else
    v_status:=v_requested;
    update bt2.bugs set status=v_status,state_version=v_state,updated_at=clock_timestamp(),closed_at=case when v_status='CLOSED' then clock_timestamp() else closed_at end where bug_id=p_bug_id;
    insert into bt2.bug_events(bug_event_id,bug_id,state_version,event_type,actor_agent_key,operation_id,details) values(v_event,p_bug_id,v_state,'STATUS_CHANGED',case when exists(select 1 from bt2.agents where agent_key=v_actor) then v_actor else null end,p_operation_id,jsonb_build_object('from_status',v_bug.status,'to_status',v_status,'note',p_note));
  end if;
  v_result:=jsonb_build_object('event_id',v_event,'state_version',v_state,'status',v_status,'queue_item_id',v_queue);
  v_result_digest:=encode(digest(convert_to(v_result::text,'UTF8'),'sha256'),'hex');
  update bt2.operations set state='VERIFIED',resolved_at=clock_timestamp(),result_payload=v_result,result_digest_sha256=v_result_digest,updated_at=clock_timestamp() where operation_id=p_operation_id;
  return query select v_event,v_state,v_status,v_queue,false;
end
$function$;
