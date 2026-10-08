#CB 30/10/2025
"""Report notebooks in this folder that are not enabled in the mkfigs.sh `array=( ... )`."""
import glob
import re

with open("mkfigs.sh") as f:
    text = f.read()

# Grab the real bash array block (line starting `array=(` up to a line that is just `)`),
# not the first line that happens to mention the word "array".
m = re.search(r"^array=\(\n(.*?)^\)", text, re.S | re.M)
if m is None:
    raise SystemExit("Could not find an `array=(` ... `)` block in mkfigs.sh")

enabled, disabled = set(), set()
for line in m.group(1).splitlines():
    line = line.strip()
    if not line:
        continue
    if line.startswith("#"):  # commented-out entry, e.g. `#wombatlite_global #reason`
        name = line.lstrip("#").split()[0] if line.lstrip("#").strip() else ""
        if name:
            disabled.add(name + ".ipynb")
        continue
    enabled.add(line.split("#")[0].split()[0] + ".ipynb")  # drop inline comments

actual = set(glob.glob("*.ipynb"))

print(f"Enabled in mkfigs.sh ({len(enabled)}):", sorted(enabled))
print(f"\nCommented out in mkfigs.sh ({len(disabled & actual)}):", sorted(disabled & actual))
print(f"\nIn folder but not in mkfigs.sh at all ({len(actual - enabled - disabled)}):",
      sorted(actual - enabled - disabled))
print(f"\nIn mkfigs.sh but no such notebook ({len(enabled - actual)}):", sorted(enabled - actual))
