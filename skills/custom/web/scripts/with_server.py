#!/usr/bin/env python3
"""
Start one or more servers, wait for them to be ready, run a command, then clean up.

Usage:
    # Single server
    python scripts/with_server.py --server "npm run dev" --port 5173 -- python automation.py
    python scripts/with_server.py --server "npm start" --port 3000 -- python test.py

    # Multiple servers requiring shell operators
    python scripts/with_server.py \
      --shell-server "cd backend && python server.py" --port 3000 \
      --shell-server "cd frontend && npm run dev" --port 5173 \
      -- python test.py
"""

import os
import signal
import subprocess
import socket
import time
import sys
import shlex
import argparse


def parse_server_command(command):
    """Parse a server command into an argument list without a shell."""
    command_args = shlex.split(command)
    if not command_args:
        raise argparse.ArgumentTypeError('Serverbefehl darf nicht leer sein')
    return {'cmd': command_args, 'display': command, 'shell': False}


def parse_shell_server_command(command):
    """Keep an operator-authored command for explicit shell execution."""
    if not command.strip():
        raise argparse.ArgumentTypeError('Shell-Serverbefehl darf nicht leer sein')
    return {'cmd': command, 'display': command, 'shell': True}


def is_server_ready(port, process, timeout=30):
    """Wait for server to be ready by polling the port."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        return_code = process.poll()
        if return_code is not None:
            raise RuntimeError(f"Serverprozess wurde mit Exit-Code {return_code} beendet, bevor Port {port} bereit war")
        try:
            with socket.create_connection(('localhost', port), timeout=1):
                return_code = process.poll()
                if return_code is not None:
                    raise RuntimeError(f"Serverprozess wurde mit Exit-Code {return_code} beendet, bevor Port {port} bereit war")
                return True
        except (socket.error, ConnectionRefusedError):
            time.sleep(0.5)
    return False


def process_group_options():
    """Return platform-specific Popen options for an isolated process group."""
    if sys.platform == 'win32':
        return {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP}
    return {'start_new_session': True}


def stop_process_group(process):
    """Stop the server process and all children in its process group."""
    if sys.platform == 'win32':
        if process.poll() is None:
            subprocess.run(
                ['taskkill', '/PID', str(process.pid), '/T', '/F'],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            process.wait()
        else:
            try:
                os.kill(process.pid, signal.CTRL_BREAK_EVENT)
            except OSError:
                pass
        return

    try:
        os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=5)
    except ProcessLookupError:
        process.wait()
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()


def main():
    parser = argparse.ArgumentParser(description='Run command with one or more servers')
    parser.add_argument('--server', action='append', dest='servers', type=parse_server_command, help='Serverbefehl ohne Shell (wiederholbar)')
    parser.add_argument('--shell-server', action='append', dest='servers', type=parse_shell_server_command, help='Vertrauenswürdiger Operatorbefehl mit erforderlicher Shell-Syntax (wiederholbar)')
    parser.add_argument('--port', action='append', dest='ports', type=int, required=True, help='Port pro Serveroption')
    parser.add_argument('--timeout', type=int, default=30, help='Timeout in seconds per server (default: 30)')
    parser.add_argument('command', nargs=argparse.REMAINDER, help='Command to run after server(s) ready')

    args = parser.parse_args()

    if not args.servers:
        parser.error('mindestens eine Option --server oder --shell-server ist erforderlich')

    # Remove the '--' separator if present
    if args.command and args.command[0] == '--':
        args.command = args.command[1:]

    if not args.command:
        print("Error: No command specified to run")
        sys.exit(1)

    # Parse server configurations
    if len(args.servers) != len(args.ports):
        print("Error: Number of --server and --port arguments must match")
        sys.exit(1)

    servers = []
    for command, port in zip(args.servers, args.ports):
        servers.append({**command, 'port': port})

    server_processes = []

    try:
        # Start all servers
        for i, server in enumerate(servers):
            print(f"Starting server {i+1}/{len(servers)}: {server['display']}")

            # Inherit stdout/stderr so high-volume servers cannot fill an unread pipe.
            process = subprocess.Popen(
                server['cmd'],
                shell=server['shell'],
                **process_group_options()
            )
            server_processes.append(process)

            # Wait for this server to be ready
            print(f"Waiting for server on port {server['port']}...")
            if not is_server_ready(server['port'], process, timeout=args.timeout):
                raise RuntimeError(f"Server failed to start on port {server['port']} within {args.timeout}s")

            print(f"Server ready on port {server['port']}")

        print(f"\nAll {len(servers)} server(s) ready")

        # Run the command
        print(f"Running: {' '.join(args.command)}\n")
        result = subprocess.run(args.command)
        sys.exit(result.returncode)

    finally:
        # Clean up all servers
        print(f"\nStopping {len(server_processes)} server(s)...")
        for i, process in enumerate(server_processes):
            stop_process_group(process)
            print(f"Server {i+1} stopped")
        print("All servers stopped")


if __name__ == '__main__':
    main()
