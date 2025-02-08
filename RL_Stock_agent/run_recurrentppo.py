import numpy as np

from sb3_contrib import RecurrentPPO
from stable_baselines3.common.callbacks import BaseCallback

import datetime
import os
import logging
from stock_Env import Env
from mt5 import MT5_Link as link
import MetaTrader5 as mt5
from stable_baselines3.common.env_util import make_vec_env


LOGGING_LEVEL = logging.DEBUG

class CustomCallback(BaseCallback):
    """
    Custom callback class for logging and extending training behavior in reinforcement
    learning environments.

    This class provides a mechanism to log important metrics, such as average cash in
    hand, average reward, and average total net worth, during each training step.
    It enables additional custom operations to be performed at each step by overriding
    the `_on_step` method. This is particularly useful for monitoring and debugging
    training processes in trading environments.

    Attributes:
        verbose (int): Verbosity level of the callback. Determines the amount
            of logging information displayed during training.
    """
    def __init__(self, verbose: int = 0):
        super(CustomCallback, self).__init__(verbose)

    def _on_step(self) -> bool:
        """
        Logs key trading metrics at each step during training and provides a hook for
        customized operations.

        This function retrieves key metrics including the average cash in hand, average
        reward, and average total net worth from the training environment. These metrics
        are then recorded using the logger for tracking purposes. This hook method can
        be used for additional custom operations during training and must return a boolean
        value indicating the outcome.

        Returns:
            bool: Always returns True to indicate the successful execution of this hook.
        """
        cash_left = np.mean(self.training_env.get_attr("cash_in_hand"))
        reward = np.mean(self.training_env.get_attr("reward"))
        total_net = np.mean(self.training_env.get_attr("total_net"))

        self.logger.record("cash_in_hand - ", cash_left)
        self.logger.record("reward - ", reward)
        self.logger.record("Total Net - ", total_net)
        
        return True


def main() -> None:
    """
    Initializes and configures logging, sets up the environment, loads or creates a Recurrent PPO
    agent for reinforcement learning, trains the agent, saves the model, and evaluates the agent
    by interacting with the environment.

    This function demonstrates the complete process of setting up a reinforcement learning agent,
    training it, and testing its performance in the environment. It handles the configuration of
    logging for debugging and analysis, preparation of the environment, loading of an existing
    agent if present, or the training of a new one. It also saves the trained agent model and
    evaluates its performance by interacting with the environment after training.

    Args:
        None

    Returns:
        None

    Raises:
        FileNotFoundError: If specified file paths for loading the model or logging configuration
        are not found.

    """
    # logging
    now = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
    logging.basicConfig(filename=f'saved_Files/log_files/{now}_RPPO_log.log',
                        level=LOGGING_LEVEL,
                        format='%(asctime)s :: %(levelname)s :: %(module)s :: %(processName)s'
                               ' :: %(funcName)s :: line #-%(lineno)d :: %(message)s')
    # env = GenEnv(data)
    env = make_vec_env(Env, n_envs=1)

    if os.path.exists("saved_Files/saved_model/Rec_PPO"):
        agent = RecurrentPPO.load("saved_Files/saved_model/Rec_PPO")
    else:
        # running a recurrentPPO agent
        agent = RecurrentPPO('MlpLstmPolicy', env, verbose=1, tensorboard_log="saved_Files/logs", device="cuda")
    
    # train the agent 
    agent.learn(total_timesteps=10000, callback=CustomCallback())
    
    # save the trained agent
    agent.save("saved_Files/saved_model/Rec_PPO")

    # load the saved agent
    agent = RecurrentPPO.load("saved_Files/saved_model/Rec_PPO")
    
    # reset env
    obs = env.reset()
    
    # evaluate 
    for _ in range(15):
        action, _ = agent.predict(obs)
        obs, rewards, _, _ = env.step(action)
        
    

if __name__ == '__main__':
    main()
    
    #logging
    now = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
    logging.basicConfig(filename=f'saved_Files/log_files/{now}.log',
                        level=LOGGING_LEVEL,
                        format='%(asctime)s :: %(levelname)s :: %(module)s :: %(processName)s'
                               ' :: %(funcName)s :: line #%(lineno)d :: %(message)s')


