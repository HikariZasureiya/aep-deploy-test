import os
import json
import aepp
from aepp import sandboxes
from dotenv import load_dotenv

load_dotenv()

# 1. Read Credentials & Sandboxes
client_id = os.getenv("AEP_CLIENT_ID").strip()
secret = os.getenv("AEP_CLIENT_SECRET").strip()
tech_id = os.getenv("AEP_TECHNICAL_ACCOUNT_ID","").strip()
org_id = os.getenv("AEP_IMS_ORG_ID").strip()

# Technical Sandbox Names
source_sandbox = os.getenv("AEP_SOURCE_SANDBOX", "cts-utility-demo-2").strip()
target_sandbox = os.getenv("AEP_TARGET_SANDBOX", "prod").strip()

# 2. Load Package JSON
package_file_path = "./package/package.json"
with open(package_file_path, "r", encoding="utf-8") as f:
    committed_package_data = json.load(f)

package_id = committed_package_data["versions"][-1]["package_id"]
print(f"Deploying Package ID: {package_id}")

scopes_list = [
    "openid",
    "AdobeID",
    "read_organizations",
    "additional_info.projectedProductContext",
    "session",
    "https://ims-na1.adobelogin.com/s/ent_dataservices_sdk"
]

# 3. Configure aepp Connection
config_instance = aepp.configure(
    org_id=org_id,
    tech_id=tech_id,
    secret=secret,
    client_id=client_id,
    scopes=scopes_list,
    sandbox=source_sandbox,
    environment="prod",
    region="va7",
    connectInstance=True
)

try:
    # 4. Instantiate Sandboxes class
    sb_manager = sandboxes.Sandboxes(config=config_instance)

    # Retrieve package from source sandbox
    latest_package = sb_manager.getPackage(package_id)
    print("Package Retrieved Successfully:", latest_package.get("name"))

    # Wrap package
    pkgManager = sandboxes.PackageManager(package=latest_package, config=config_instance)

    # 5. Conflict Check against Target Sandbox
    print(f"Checking conflicts for import into '{target_sandbox}'...")
    conflicts = sb_manager.importPackageCheck(
        packageId=pkgManager.id,
        targetSandbox=target_sandbox
    )
    print("Conflict Check Output:", conflicts)

    # 6. Execute Import
    print(f"Importing package '{pkgManager.id}' into '{target_sandbox}'...")
    import_result = sb_manager.importPackage(
        packageId=pkgManager.id,
        targetSandbox=target_sandbox
    )
    print("Package Import Successful:", import_result)

except Exception as e:
    print("API Execution Error:", e)