from ragas.metrics import ToolCallAccuracy
from ragas.dataset_schema import MultiTurnSample
from ragas.messages import HumanMessage, AIMessage, ToolMessage, ToolCall

"""
I think the sample would come from a real interaction with the news-search app, but I would
have to save the entire interaction to a file and then load it here to compare with the reference.
"""
sample = [
    HumanMessage(content="Why is the sky blue?"),
    AIMessage(
        content="""
Here are some interesting articles that explain why the sky is blue:                                                         

 1 Why Is The Sky Blue? The Answer Is More Complex Than You Might Think - ScienceAlert                                       
   This article discusses how the blue portion of sunlight is more likely to bounce off the molecules in the atmosphere,     
   leading to the blue appearance of the sky. It references the work of British physicist Lord Rayleigh, who explained that  
   blue light is scattered more efficiently than other colors.                                                               
 2 Why Is the Sky Blue? | NASA Space Place                                                                                   
   This resource explains that blue light travels as shorter, smaller waves and is scattered in all directions by air        
   molecules. It also describes how the sky can appear red during sunrise and sunset due to the scattering of light.         
 3 Curious Kids: Why is the sky blue? | University of Wisconsin - Stout                                                      
   This article provides a simple explanation suitable for kids, emphasizing that blue light is scattered across the sky,    
   while other colors mainly travel straight through the atmosphere.                                                         
 4 Why is the sky blue? - Space.com                                                                                          
   This piece explains the phenomenon of Rayleigh scattering and how it affects the color of the sky, noting that in outer   
   space, the sky appears black even in sunlight.                                                                            
 5 Why Is the Sky Blue? | Britannica                                                                                         
   This article from Encyclopedia Britannica discusses the role of air molecules and dust particles in scattering shorter    
   wavelengths of light, which contributes to the blue color of the sky.                                                     

These articles provide a comprehensive understanding of the science behind the blue sky!         
        """,
        tool_calls=[
            ToolCall(name="web_search", args={"query": "Why is the sky blue?"})
        ],
    ),
]

sample = MultiTurnSample(
    user_input=sample,
    reference_tool_calls=[
        ToolCall(name="web_search", args={"query": "Why is the sky blue?"})
    ],
)


async def evaluate_sample():
    scorer = ToolCallAccuracy()
    return await scorer.multi_turn_ascore(sample)


# Run the async function
import asyncio

result = asyncio.run(evaluate_sample())
print(result)
