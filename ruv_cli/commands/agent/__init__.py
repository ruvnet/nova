from .code_agent import run_code
from .data_agent import run_data_operation
from .employee_agent import manage_employee_agent
from .comms_agent import handle_communication

def handle_agent_command(args):
    """Route agent commands to appropriate handlers"""
    if args.agent_cmd == "code":
        query = " ".join(args.query) if args.query else ""
        success = run_code(query)
        return success
    elif args.agent_cmd == "data":
        success = run_data_operation(
            operation=args.operation,
            file_path=args.file,
            columns=args.columns
        )
        return success
    elif args.agent_cmd == "employee":
        success = manage_employee_agent(
            role=args.role,
            start=args.start,
            stop=args.stop,
            status=args.status
        )
        return success
    elif args.agent_cmd == "comms":
        success = handle_communication(
            method=args.method,
            message=args.message
        )
        return success
    else:
        print("[ERROR] Unknown agent subcommand.")
        return False