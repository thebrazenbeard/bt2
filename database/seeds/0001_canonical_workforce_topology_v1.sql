-- Canonical BT2 workforce topology seed V1.
-- Reconstructs the accepted 3-unit / 13-agent / 14-edge topology from source.
-- Replay is allowed only when the resulting semantic subject is identical.

BEGIN;
SET CONSTRAINTS ALL DEFERRED;

INSERT INTO bt2.agent_units(
  unit_key,display_name,unit_type,orchestrator_agent_key,active,description
) VALUES
  ('build_team','Build Team Two','ORCHESTRATED_TEAM','one',true,'Primary One-led workforce; Two, Three, Four, Five, Six, Seven, Eight, Nine, and Thirteen operate as specialist subagents.'),
  ('hephaestus','Hephaestus','INDEPENDENT_AGENT',NULL,true,'Independent Project-engineering specialist operating outside One subagent hierarchy.'),
  ('masamune','Masamune','PAIRED_TEAM',NULL,true,'Independent debugger/reliability pair consisting of Masa and Mune.')
ON CONFLICT (unit_key) DO NOTHING;

INSERT INTO bt2.agents(
  agent_key,display_name,numerical_identity,unit_key,role_kind,role_summary,active,training_required
) VALUES
  ('one','One',1,'build_team','PRIMARY','Primary BT2 orchestrator: governance, delegation, integration, synthesis, currentness discipline, and final collective decision.',true,true),
  ('two','Two',2,'build_team','SUBAGENT','Structural and systems architecture specialist: boundaries, dependencies, data architecture, and hidden coupling.',true,true),
  ('three','Three',3,'build_team','SUBAGENT','Implementation and realizability specialist: concrete execution, PostgreSQL/provider implementation, and operational proof.',true,true),
  ('four','Four',4,'build_team','SUBAGENT','Protocol, alternatives, minimality, and architecture-challenge specialist.',true,true),
  ('five','Five',5,'build_team','SUBAGENT','Evidence, source provenance, exact currentness, release, and effect-state specialist.',true,true),
  ('six','Six',6,'build_team','SUBAGENT','Runtime, resource, operational feasibility, and human-operability specialist.',true,true),
  ('seven','Seven',7,'build_team','SUBAGENT','Security, safety, permission, privacy, abuse-path, and adversarial specialist.',true,true),
  ('eight','Eight',8,'build_team','SUBAGENT','Pragmatic maintainability, cost, evidence sufficiency, and tradeoff specialist.',true,true),
  ('nine','Nine',9,'build_team','SUBAGENT','Acceptance, falsification, regression, reproducibility, and adversarial-test specialist.',true,true),
  ('thirteen','Thirteen',13,'build_team','SUBAGENT','Independent dissent specialist: premise attack, authority correction, consensus challenge, and claim-ceiling pressure.',true,true),
  ('masa','Masa',NULL,'masamune','PAIRED','Root-cause, incident, reliability, and causal-debugging agent.',true,true),
  ('mune','Mune',NULL,'masamune','PAIRED','Independent reproduction, fix verification, regression, and adversarial implementation-review agent.',true,true),
  ('hephaestus','Hephaestus',NULL,'hephaestus','INDEPENDENT','Independent native-ChatGPT Project engineering, migration, repair, qualification, and rollback specialist.',true,true)
ON CONFLICT (agent_key) DO NOTHING;

INSERT INTO bt2.agent_relationships(source_agent_key,target_agent_key,relation_type,active)
VALUES
  ('one','two','ORCHESTRATES',true),
  ('one','three','ORCHESTRATES',true),
  ('one','four','ORCHESTRATES',true),
  ('one','five','ORCHESTRATES',true),
  ('one','six','ORCHESTRATES',true),
  ('one','seven','ORCHESTRATES',true),
  ('one','eight','ORCHESTRATES',true),
  ('one','nine','ORCHESTRATES',true),
  ('one','thirteen','ORCHESTRATES',true),
  ('one','masa','COORDINATES_WITH',true),
  ('one','mune','COORDINATES_WITH',true),
  ('one','hephaestus','COORDINATES_WITH',true),
  ('masa','mune','PAIRED_WITH',true),
  ('mune','masa','PAIRED_WITH',true)
ON CONFLICT (source_agent_key,target_agent_key,relation_type) DO NOTHING;

DO $verify$
DECLARE
  v_digest text;
BEGIN
  IF (SELECT count(*) FROM bt2.agent_units) <> 3
     OR (SELECT count(*) FROM bt2.agents) <> 13
     OR (SELECT count(*) FROM bt2.agent_relationships) <> 14 THEN
    RAISE EXCEPTION 'BT2_CANONICAL_TOPOLOGY_CARDINALITY_MISMATCH';
  END IF;

  WITH topo AS (
    SELECT jsonb_build_object(
      'units',(SELECT jsonb_agg(jsonb_build_array(unit_key,display_name,unit_type,orchestrator_agent_key,active,description) ORDER BY unit_key) FROM bt2.agent_units),
      'agents',(SELECT jsonb_agg(jsonb_build_array(agent_key,display_name,numerical_identity,unit_key,role_kind,role_summary,active,training_required) ORDER BY agent_key) FROM bt2.agents),
      'relationships',(SELECT jsonb_agg(jsonb_build_array(source_agent_key,target_agent_key,relation_type,active) ORDER BY source_agent_key,target_agent_key,relation_type) FROM bt2.agent_relationships)
    ) AS doc
  )
  SELECT encode(public.digest(convert_to(doc::text,'UTF8'),'sha256'),'hex') INTO v_digest FROM topo;

  IF v_digest <> '45d262aae7285a69a66a3d5b35c04537899ba33f5eb7388b9731071e8907c0d8' THEN
    RAISE EXCEPTION 'BT2_CANONICAL_TOPOLOGY_DIGEST_MISMATCH:%',v_digest;
  END IF;
END
$verify$;

COMMIT;
