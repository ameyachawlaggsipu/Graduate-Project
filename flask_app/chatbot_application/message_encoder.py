from langchain_core.messages import HumanMessage, AIMessage


class MessageEncoder:
    def __init__(self, message):
        self.message = message

    def to_dict(self):
        return {
            "type": "AIMessage" if isinstance(self.message, AIMessage) else "HumanMessage",
            "content": self.message.content
        }

    @staticmethod
    def from_dict(data):
        if data["type"] == "AIMessage":
            return AIMessage(data["content"])
        elif data["type"] == "HumanMessage":
            return HumanMessage(data["content"])
        else:
            # Handle unknown message type or missing data
            raise ValueError("Unknown message type or missing data in 'from_dict'")
