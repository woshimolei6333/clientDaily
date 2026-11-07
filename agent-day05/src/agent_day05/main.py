from agent_day05.agent_old import StockAgentOld

def main():

    agent = StockAgentOld()
    while True:
        question = input("\n请输入问题 (exit推出)")

        if question.lower() == "exit":
            break

        try:
            answer = agent.run(question)
            print("\nAgent: ")
            print(answer)
        except Exception as error:
            print(f"运行失败: {error}")
if __name__ == '__main__':
    main()