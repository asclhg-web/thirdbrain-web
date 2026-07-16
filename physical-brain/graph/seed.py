"""샘플 볼트를 그래프에 시드."""
import os

from pipelines.vault_sync import sync_vault

if __name__ == "__main__":
    vault = os.path.join(os.path.dirname(__file__), "sample_vault")
    result = sync_vault(vault)
    print("시드 완료:", result)
