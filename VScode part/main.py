from agent.agent import Agent
from tools import create_tool_registry


def print_banner():
  
    print("1. Agent Mode")
    print("2. General Chat")
    print("3. Exit")
    


def agent_mode(agent):
    print()
    print("=== AGENT MODE ===")
    print("Type 'back' to return to the main menu.")
    print()

    while True:

        task = input("You: ").strip()

        if not task:
            continue

        if task.lower() == "back":
            break

        agent.run(task)


def general_chat():
    from model_client import ask_model

    print()
    print("=== GENERAL CHAT ===")
    print("Type 'back' to return to the main menu.")
    print()

    while True:

        message = input("You: ").strip()

        if not message:
            continue

        if message.lower() == "back":
            break

        try:
            response = ask_model(
                message,
                max_new_tokens=512,
                temperature=0.5,
            )

            print()
            print("AI:")
            print(response)
            print()

        except Exception as e:

            print()
            print(f"Model error: {e}")
            print()


def main():

    registry = create_tool_registry()

    agent = Agent(
        registry
    )

    while True:

        print_banner()

        choice = input(
            "Select an option: "
        ).strip()

        if choice == "1":

            agent_mode(
                agent
            )

        elif choice == "2":

            general_chat()

        elif choice == "3":

            print()
            print("Goodbye!")
            break

        else:

            print()
            print("Invalid option.")


if __name__ == "__main__":
    main()