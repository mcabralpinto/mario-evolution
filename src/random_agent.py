import src.marioai as marioai
import src.agents as agents
import src.tasks.runner as runner

def main():
    agent = agents.RandomAgent()
    task = runner.RunnerTask(visualization=True)
    exp = marioai.Experiment(task, agent)
    
    exp.max_fps = -1
    task.env.level_type = 0
    rewards = exp.doEpisodes()
    print(sum(rewards[0]))


if __name__ == '__main__':
    main()