"""Event service example."""

from .event_service import EventService


def main():
    print("\n" + "="*60)
    print("Event Service Example")
    print("="*60 + "\n")

    event_service = EventService()

    def on_message(data):
        print(f"Received: {data['message']}")

    event_service.subscribe("message", on_message)
    event_service.emit("message", {"message": "Hello Events!"})
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
