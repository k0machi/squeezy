from config import ENVIRONMENT
from pathlib import Path


def basic_config():
    template_path = Path(ENVIRONMENT.get(
        "INSTANCE_PATH") + ENVIRONMENT.get("SQUID_TEMPLATE_DIR") + "/squid.conf.default")

    with open(template_path, "rt") as f:
        template = f.read()

    squid_config_keys = [(key, value) for key, value in ENVIRONMENT.items() if key.startswith("SQUEEZY_SQUID_CONFIG")]
    for key, value in squid_config_keys:
        template = template.replace(f"${key}", value, 1)

    config_path = Path(ENVIRONMENT.get("INSTANCE_PATH") +
                        ENVIRONMENT.get("SQUID_CONFIG_DIR") + "/squid.conf")
    with open(config_path, "w+t") as f:
        f.write(template)

if __name__ == "__main__":
    basic_config()