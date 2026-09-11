#!/usr/bin/env python3
import hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parent
M=ROOT/"training_manifest.json"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 m=json.loads(M.read_text(encoding="utf-8"))
 rows=[]
 for rel,meta in m["file_inventory"].items():
  p=ROOT/rel
  if not p.is_file(): print("FAIL missing",rel); return 2
  b=p.read_bytes(); s=hashlib.sha256(b).hexdigest()
  if s!=meta["sha256"] or len(b)!=meta["bytes"]: print("FAIL mismatch",rel); return 2
  rows.append((rel,s,len(b)))
 enc="".join(f"{a}\0{b}\0{c}\n" for a,b,c in sorted(rows)).encode()
 d=hashlib.sha256(enc).hexdigest()
 if d!=m["source_set_digest_sha256"]: print("FAIL source_set_digest",d); return 2
 mods=[x["path"] for x in m["module_order"]]
 if mods[-1]!="modules/09_final_qualification.md" or len(mods)!=9: print("FAIL module order"); return 2
 print("PASS",m["package_id"],m["version"],d); return 0
if __name__=="__main__": raise SystemExit(main())
