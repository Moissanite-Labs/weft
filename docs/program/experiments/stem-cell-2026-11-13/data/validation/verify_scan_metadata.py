"""Verify that four scanner findings are source SHA metadata, without printing values."""
import hashlib,json,re,subprocess
from pathlib import Path
record=Path(__file__).with_name("secret-scan-false-positives.json")
for row in json.loads(record.read_text())["findings"]:
 commit,path,rule,line=row["fingerprint"].split(":")
 text=subprocess.check_output(["git","show",commit+":"+path],text=True).splitlines()[int(line)-1]
 m=re.search(r'"(api_worker\.py|test_api_worker\.py)":\s*"([0-9a-f]{64})"',text)
 assert m and m.group(1)==row["source_file"]
 assert hashlib.sha256(m.group(2).encode()).hexdigest()==row["sha256_of_reported_value"]
print(json.dumps({"verified_source_metadata_false_positives":4,"values_printed":False}))
