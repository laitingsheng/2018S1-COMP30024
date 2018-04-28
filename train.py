import numpy as np
import tensorflow as tf

import Player
import Random
from Evaluation import TrainEvaluation


class TDSelfPlayer(Player.Player):
    def __init__(self, depth=4, ep=0.2, la=0.7):
        super().__init__(depth=depth, model=TrainEvaluation())

        for tvar in self.model.trainable_variables:
            tf.summary.histogram(tvar.op.name, tvar)

        with tf.name_scope('random_agent_test_results'):
            self.w_wins_ = tf.placeholder(tf.int32, name='w_wins_')
            self.w_wins = tf.Variable(0, name="w_wins", trainable=False)

            self.w_draws_ = tf.placeholder(tf.int32, name='w_draws_')
            self.w_draws = tf.Variable(0, name="w_draws", trainable=False)

            self.w_losses_ = tf.placeholder(tf.int32, name='w_losses_')
            self.w_losses = tf.Variable(0, name="w_losses", trainable=False)

            self.b_wins_ = tf.placeholder(tf.int32, name='b_wins_')
            self.b_wins = tf.Variable(0, name="b_wins", trainable=False)

            self.b_draws_ = tf.placeholder(tf.int32, name='b_draws_')
            self.b_draws = tf.Variable(0, name="b_draws", trainable=False)

            self.b_losses_ = tf.placeholder(tf.int32, name='b_losses_')
            self.b_losses = tf.Variable(0, name="b_losses", trainable=False)

            self.update_w_wins = tf.assign(self.w_wins, self.w_wins_)
            self.update_w_draws = tf.assign(self.w_draws, self.w_draws_)
            self.update_w_losses = tf.assign(self.w_losses, self.w_losses_)

            self.update_b_wins = tf.assign(self.b_wins, self.b_wins_)
            self.update_b_draws = tf.assign(self.b_draws, self.b_draws_)
            self.update_b_losses = tf.assign(self.b_losses, self.b_losses_)

            self.update_random_agent_test_results = tf.group(
                self.update_w_wins, self.update_w_draws, self.update_w_losses,
                self.update_b_wins, self.update_b_draws, self.update_b_losses
            )
            self.random_agent_test_s = [self.w_wins_,
                                        self.w_draws_,
                                        self.w_losses_,
                                        self.b_wins_,
                                        self.b_draws_,
                                        self.b_losses_]

            tf.summary.scalar("w_wins", self.w_wins)
            tf.summary.scalar("w_draws", self.w_draws)
            tf.summary.scalar("w_losses", self.w_losses)

            tf.summary.scalar("b_wins", self.b_wins)
            tf.summary.scalar("b_draws", self.b_draws)
            tf.summary.scalar("b_losses", self.b_losses)

        self.opt = tf.train.AdamOptimizer()
        self.grads = tf.gradients(
            self.model.value, self.model.trainable_variables
        )
        self.grads_s = [
            tf.placeholder(tf.float32, shape=tvar.get_shape())
            for tvar in self.model.trainable_variables
        ]
        self.apply_grads = self.opt.apply_gradients(
            zip(self.grads_s, self.model.trainable_variables),
            name='apply_grads'
        )

    def _eval(self, board):
        return self.sess.run(
            self.model.value,
            feed_dict={self.model.feature_vector_: board.feature_vector}
        )[0, 0]

    def train(self):
        self.board.__init__()

        traces = [
            np.zeros(tvar.shape)
            for tvar in self.model.trainable_variables
        ]
        feature_vector = self.board.feature_vector

        prev_leaf_value, prev_grads = self.sess.run(
            [self.model.value, self.grads],
            feed_dict={self.model.feature_vector_: feature_vector}
        )
        reward = self.board.reward()

        while reward is None:
            if self.board.placing:
                pos, leaf_value = self._place(True)
                if np.random.rand() < epsilon:
                    self.board.place(*self._place_random())
                else:
                    self.board.place(*pos)
            else:
                action, leaf_value = self._move(True)
                if action is None:
                    self.board.forfeit_move()
                else:
                    if np.random.rand() < epsilon:
                        src, dest = self._move_random()
                    else:
                        src, dest = action
                    self.move(*src, *dest)

            reward = self.board.reward()
            feature_vector = self.board.feature_vector
            grads = self.sess.run(
                self.grads, feed_dict={
                    self.model.feature_vector_: feature_vector
                }
            )

            delta = leaf_value - prev_leaf_value
            for prev_grad, trace in zip(prev_grads, traces):
                trace *= lamda
                trace += prev_grad

            self.sess.run(
                self.apply_grads, feed_dict={
                    grad_: -delta * trace
                    for grad_, trace in zip(self.grads_s, traces)
                }
            )

            prev_grads = grads
            prev_leaf_value = leaf_value

        return self.board.reward()


def main():
    rp = Random.Player()
    p = TDSelfPlayer()

    log_dir = "./log/leaf"
    summary_op = tf.summary.merge_all()
    summary_writer = tf.summary.FileWriter(log_dir)

    episode_count = tf.train.get_or_create_global_step()
    increment_episode_count = tf.assign_add(episode_count, 1)

    scaffold = tf.train.Scaffold(summary_op=summary_op)
    with tf.train.MonitoredTrainingSession(checkpoint_dir=log_dir,
                                           scaffold=scaffold) as sess:
        p.sess = sess
        while True:
            count = sess.run(episode_count)
            if count % 1000 == 0:
                results = rp.test(p)

                sess.run(
                    p.update_random_agent_test_results,
                    feed_dict={
                        random_agent_test_: result
                        for random_agent_test_, result in zip(
                            p.random_agent_test_s, results
                        )
                    }
                )
                print(f"{count}: {results}")

                if results[2] + results[5] == 0:
                    final_summary = sess.run(summary_op)
                    summary_writer.add_summary(
                        final_summary, global_step=episode_count
                    )
                    break
            else:
                p.train()
            sess.run(increment_episode_count)


if __name__ == "__main__":
    main()
