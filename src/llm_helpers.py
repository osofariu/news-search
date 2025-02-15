from langgraph.graph import MessagesState, StateGraph

def get_last_message(state: MessagesState):
        messages = state.get("messages", [])
        if messages:
            return messages[-1]
        else:
            raise ValueError("There is no last message (empty list)")

def get_last_content(state: MessagesState):
    last_message = get_last_message(state)
    return last_message.content
    
def next_node_is_human(graph: StateGraph, config):
    next_node = graph.get_state(config).next
    if (len(next_node) > 0 and next_node[0] == 'human_input'):
        return True
    return False

def last_message_has_tool_calls(state: MessagesState):
    last_message = get_last_message(state)
    args = last_message.additional_kwargs
    if args.get("tool_calls"):
        return True
    else:
        return False
    

def last_message_is_ask_for_human_input(state: MessagesState):
    """determine if we need human input
    
    This is a bit if a hack.. maybe we can improve it
    
    Not sure of a good way to tell if the response from the model is a
    refined answer from tool calls or it's asking for more information:
    if it's a short message then it's probably asking for help..
    """
    last_message = get_last_message(state)
    response_metadata = last_message.response_metadata 
    token_usage = response_metadata.get("token_usage")
    completion_tokens = token_usage.get("completion_tokens") or 0
    return completion_tokens < 100
