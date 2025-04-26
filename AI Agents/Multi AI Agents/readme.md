# Multi-Agent Project Simulation using Semantic Kernel and OpenAI

This project demonstrates a **multi-agent workflow** using the Microsoft [Semantic Kernel](https://github.com/microsoft/semantic-kernel) with OpenAI GPT-4o, simulating a real-world software development pipeline.  
It features three distinct AI agents:
- **Program Manager Agent**: Gathers user requirements and prepares a project plan.
- **Software Engineer Agent**: Builds a web application based on the plan.
- **Project Manager Agent**: Reviews and approves the final deliverable.

---

## How It Works
* **Kernel Initialization:** Set up a Kernel instance using OpenAI's GPT-4o model.
* **Agent Roles:** Three agents are created with different instructions:
* **Program Manager:** Gathers requirements.
* **Software Engineer:** Builds based on specs.
* **Project Manager:** Reviews and approves.
* **Group Chat:** All agents are placed in a shared AgentGroupChat.
* **Custom Termination:** Conversation automatically ends once the Project Manager replies with "approve".
* **Execution:** A user prompt is injected, and the agents start their workflow until the task is completed and approved.

## Notes
* This example is simplified for demonstration purposes.
* In real-world applications, you can add more agents like **UI/UX Designer, QA Tester, or DevOps Engineer**.
* Always monitor API usage to avoid unexpected charges when using OpenAI services.
* Current Semantic Kernel packages are in **alpha**; APIs might change in future releases.