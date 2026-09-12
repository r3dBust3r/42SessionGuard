from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from secrets import choice
from string import ascii_letters, digits
import requests
import subprocess
import sys


APP_NAME = "42SessionGuard"
DATA_DIR = (Path.home() / ".local" / "share" / APP_NAME)
TOPIC_FILE = DATA_DIR / "topic"
PROFILE_FILE = Path.home() / ".profile"
NTFY_URL = "https://ntfy.sh"
TOPIC_LENGTH = 48


@dataclass
class LoginInfo:
    hostname: str
    ip: str
    login_time: str


def generate_topic() -> str:
    chars = ascii_letters + digits
    return "".join(
        choice(chars)
        for _ in range(TOPIC_LENGTH)
    )


def save_topic(topic: str) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True,)
    TOPIC_FILE.write_text(topic, encoding="utf-8")
    TOPIC_FILE.chmod(0o600)


def load_topic() -> str | None:
    if not TOPIC_FILE.exists():
        return None

    topic = TOPIC_FILE.read_text(
        encoding="utf-8",
    ).strip()

    if not topic:
        return None

    return topic


def get_or_create_topic() -> str:
    """Return the existing topic or create a new one."""

    topic = load_topic()

    if topic is not None:
        return topic

    topic = generate_topic()
    save_topic(topic)

    return topic


def run_command(command: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    return (result.returncode, result.stdout, result.stderr)


def get_hostname() -> str:
    returncode, stdout, _ = run_command(["hostname"])

    if returncode != 0:
        return "unknown"

    return stdout.strip() or "unknown"


def get_local_ip() -> str:
    returncode, stdout, _ = run_command(["hostname", "-I"])

    if returncode != 0:
        return "unknown"

    addresses = stdout.strip().split()

    if not addresses:
        return "unknown"

    return addresses[0]


def get_login_info() -> LoginInfo:
    return LoginInfo(
        hostname=get_hostname(),
        ip=get_local_ip(),
        login_time=datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )
    )


class NtfyClient:
    def __init__(self, topic: str):
        self.topic = topic
        self.url = f"{NTFY_URL}/{topic}"

    def send(self, message: str) -> bool:
        try:
            response = requests.post(
                self.url,
                data=message.encode("utf-8"),
                timeout=10,
            )
        except requests.RequestException as error:
            print(
                f"42SessionGuard: notification failed: {error}",
                file=sys.stderr
            )
            return False

        if response.status_code != 200:
            print(
                "42SessionGuard: notification failed "
                f"({response.status_code})",
                file=sys.stderr
            )
            return False

        return True


class LoginNotification:
    def __init__(self, info: LoginInfo):
        self.info = info

    def build(self) -> str:
        return (
            "NEW LOGIN DETECTED\n\n"
            f"Host: {self.info.hostname}\n"
            f"Local IP: {self.info.ip}\n"
            f"Login Time: {self.info.login_time}\n"
        )


def is_login_hook_installed() -> bool:
    if not PROFILE_FILE.exists():
        return False

    content = PROFILE_FILE.read_text(
        encoding="utf-8",
    )

    return "# 42SessionGuard" in content


def install_login_hook() -> bool:
    if is_login_hook_installed():
        return True

    try:
        content = ""
        if PROFILE_FILE.exists():
            content = PROFILE_FILE.read_text(encoding="utf-8")

        hook = (
            "\n\n"
            "# 42SessionGuard\n"
            "42sessionguard\n"
        )

        PROFILE_FILE.write_text(
            content.rstrip() + hook,
            encoding="utf-8"
        )

    except OSError as error:
        print(
            f"42SessionGuard: cannot modify ~/.profile: {error}",
            file=sys.stderr
        )
        return False

    return True


class SetupWizard:
    def __init__(self, topic: str):
        self.topic = topic
        self.client = NtfyClient(topic)

    def display(self) -> None:
        print("42SessionGuard First Setup")
        print("." * 32)
        print()
        print("1) Install 42SessionGuard on your machine")
        print("    - Run: uv tool install git+https://github.com/r3dBust3r/42SessionGuard.git")
        print("2) Install ntfy on your phone (PlayStore / AppStore)")
        print("3) Open the ntfy application")
        print("4) Subscribe to a new topic")
        print(f"   - Your topic: {self.topic}")
        print("\nIMPORTANT: Keep this topic private\n")


    def wait_for_subscription(self) -> None:
        input(
            "Press ENTER after subscribing to the topic..."
        )

    def test_notification(self) -> bool:
        print()
        print("Sending test notification...")

        success = self.client.send(
            "42SessionGuard is working!\n\n"
            "Login notifications are now configured."
        )

        if success:
            print("Test notification sent successfully.")

        return success

    def install(self) -> bool:
        print()
        print("Installing login hook...")
        success = install_login_hook()

        if success:
            print("Login hook installed successfully.")

        return success

    def run(self) -> None:
        self.display()
        self.wait_for_subscription()

        if not self.test_notification():
            print(
                "\nSetup stopped because the test "
                "notification failed."
            )
            return

        if not self.install():
            print(
                "\nSetup stopped because the login "
                "hook could not be installed."
            )
            return

        print("\nSETUP COMPLETED")
        print(
            "42SessionGuard will notify you "
            "eachtime someone log in."
        )


class SessionGuard:
    def __init__(self):
        self.topic = load_topic()

    def is_configured(self) -> bool:
        return self.topic is not None

    def setup(self) -> None:
        topic = get_or_create_topic()
        self.topic = topic
        wizard = SetupWizard(topic)
        wizard.run()

    def notify_login(self) -> None:
        if self.topic is None:
            self.setup()
            return

        info = get_login_info()
        notification = LoginNotification(info)
        client = NtfyClient(self.topic)
        client.send(notification.build())


def print_help() -> None:
    print(
        "Usage:\n"
        "  42sessionguard            Send login notification\n"
        "  42sessionguard --setup    Run setup wizard\n"
        "  42sessionguard --help     Show this help"
    )


def main() -> None:
    guard = SessionGuard()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd in ("setup", "--setup"):
            guard.setup()
            return

        if cmd in ("--help", "-h"):
            print_help()
            return

    guard.notify_login()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        exit(1)
