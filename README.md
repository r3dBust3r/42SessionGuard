# 42SessionGuard

A small Linux tool that sends a notification to your phone whenever you or someone login to your machine.

42SessionGuard uses [ntfy](https://ntfy.sh/) to send push notifications, so you can know when a new login happens.

## What is 42SessionGuard?

42SessionGuard is a simple login notification tool designed for 42/1337 students.

When you log in:

```text
  New Login
      │
      ▼
42SessionGuard
      │
      ▼
   ntfy.sh
      │
      ▼
Phone Notification
```

Example notification:
```text
NEW LOGIN DETECTED

Host: c1r7p10
Local IP: 10.20.5.42
Login Time: 12-09-2026 19:42:31
```

## Who is it for?

42SessionGuard is mainly useful for:

* 1337/42 students who want to monitor their logins
* Cybersecurity students working on lab machines
* Anyone who wants a simple login notification

It is especially useful on shared environments where you want to know when your account is accessed.

## Requirements

* Linux
* Python 3.10+
* [uv](https://docs.astral.sh/uv/)
* An Android or iOS phone

## Installation

Clone the repository:

```bash
git clone https://github.com/r3dBust3r/42SessionGuard.git
cd 42SessionGuard
```

Then install it:

```bash
make install
```

Or install it directly with `uv`:

```bash
uv tool install git+https://github.com/r3dBust3r/42SessionGuard.git
```

## First-time setup

After installation, run:

```bash
42sessionguard --setup
```

The setup wizard will guide you through the configuration.

### 1. Install ntfy

Install **ntfy** on your phone:

* Android: Google Play Store
* iOS: App Store

### 2. Subscribe to your topic

42SessionGuard generates a random private topic for you.

You will see something like:

```text
Your topic: PaKM8XxA5GphrZBLTMZFPsRr17wSe2kRvaezO6HBg3dABKj7
```

Open ntfy on your phone and subscribe to this topic.

**Keep your topic private.**

Public ntfy topics do not require an account, so anyone who knows the topic can potentially push messages to it.

### 3. Test the notification

42SessionGuard automatically sends a test notification after setup.
If you receive it on your phone, the setup is complete.

### 4. Login notifications

The setup automatically adds:

```bash
# 42SessionGuard
$HOME/.local/bin/42sessionguard
```

to your `~/.profile`.

From then on, 42SessionGuard runs automatically when your login shell starts.

## Usage

### Run manually

```bash
42sessionguard
```

This sends a login notification immediately.

### Run setup again

```bash
42sessionguard --setup
```

or:

```bash
42sessionguard setup
```

### Show help

```bash
42sessionguard --help
```

## Makefile

The project includes a Makefile for common operations.

### Install

```bash
make install
```

Installs 42SessionGuard and starts the setup wizard.

### Run

```bash
make run
```

Runs 42SessionGuard manually.

### Help

```bash
make help
```

Displays the available command options.

### Uninstall

```bash
make uninstall
```

This removes:

* The installed `42sessionguard` command
* The login hook from `~/.profile`
* The saved ntfy topic and configuration

## Uninstall manually

If you don't have the repository anymore, you can remove it manually:

```bash
uv tool uninstall 42sessionguard
```

Remove the login hook:

```bash
sed -i '/# 42SessionGuard/d;/^\$HOME\/.local\/bin\/42sessionguard$/d' ~/.profile
```

Remove the saved configuration:

```bash
rm -rf ~/.local/share/42SessionGuard
```

## Configuration

The ntfy topic is stored locally at:

```text
~/.local/share/42SessionGuard/topic
```

The file is created with restricted permissions so that only your user can read it.

42SessionGuard does not require an account or database.

## Privacy

42SessionGuard sends the following information to your ntfy topic:

* Hostname
* Local IP address
* Login time

It does **not** send:

* Passwords
* Shell history
* Files
* Commands
* Public IP address

Your ntfy topic acts as the destination for the notifications, so keep it private.

## How it works

On login, `~/.profile` launches:

```bash
$HOME/.local/bin/42sessionguard
```

42SessionGuard then:

1. Loads the saved ntfy topic.
2. Gets the hostname.
3. Gets the local IP address.
4. Gets the current date and time.
5. Creates the notification.
6. Sends it to ntfy.
7. ntfy pushes the notification to your phone.

## Project structure

```text
42SessionGuard/
├── src/
│   ├── __init__.py
│   └── main.py
├── Makefile
├── pyproject.toml
└── README.md
```

## Why ntfy?

42SessionGuard uses ntfy because it provides a simple way to send push notifications without building a notification server or requiring a complicated API.

Learn more about ntfy in the [official documentation](https://docs.ntfy.sh/).

## Security note

42SessionGuard is intended as a lightweight notification tool, not as a complete security monitoring system.