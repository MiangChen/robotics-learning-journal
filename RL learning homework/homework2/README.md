## 运行环境
- 推荐python版本为3.8。
- 需要安装numpy, matplotlib, jupyter notebook即可完成作业；
- 也可以参考requirements.txt来进行环境的配置。

## 作业要求
- 完成所有的Exercise和Programming，注意**不要有所遗漏**。
- 下发的图片无需进行上传，但是不要忘记上传自己添加的图片（如果有的话）。



```
**Exercise 4 给定一个合法占用度量$\rho$，对应的策略是否唯一，若唯一，请证明，并用占用度量表示出该策略；若不唯一，请举出反例。**

由定义$\pi(a|s) = p(A_t = a, S_t = s)$，可知$\sum_{a} \pi(a|s) = 1$。因此 $\forall a, \forall s, $有

$$
\begin{align*}
\pi_\rho (a,s) &= \frac{\pi(a|s)}{\sum_{a'} \pi(a'|s)} \\
&= \frac{\nu^\pi (s) \pi(a|s)}{\sum_{a'} \nu^\pi (s) \pi(a'|s)} \\
&= \frac{\rho^\pi (s,a)}{\sum_{a'} \rho^\pi (s,a')}. 
\end{align*}
$$

则给定$\rho$可以确定唯一的策略$\pi_\rho$.
```

>
>
>```
>**Exercise 4 给定一个合法占用度量$\rho$，对应的策略是否唯一，若唯一，请证明，并用占用度量表示出该策略；若不唯一，请举出反例。**
>
>由定义$\pi(a|s) = p(A_t = a, S_t = s)$，可知$\sum_{a} \pi(a|s) = 1$。因此 $\forall a, \forall s, $有
>
>$$
>\begin{align*}
>\pi_\rho (a,s) &= \frac{\pi(a|s)}{\sum_{a'} \pi(a'|s)} \\
>&= \frac{\nu^\pi (s) \pi(a|s)}{\sum_{a'} \nu^\pi (s) \pi(a'|s)} \\
>&= \frac{\rho^\pi (s,a)}{\sum_{a'} \rho^\pi (s,a')}. 
>\end{align*}
>$$
>
>则给定$\rho$可以确定唯一的策略$\pi_\rho$.
>```

**Exercise 4 给定一个合法占用度量$\rho$，对应的策略是否唯一，若唯一，请证明，并用占用度量表示出该策略；若不唯一，请举出反例。**

由定义$\pi(a|s) = p(A_t = a, S_t = s)$，可知$\sum_{a} \pi(a|s) = 1$。因此 $\forall a, \forall s, $有

$$
\begin{align*}
\pi_\rho (a,s) &= \frac{\pi(a|s)}{\sum_{a'} \pi(a'|s)} \\
&= \frac{\nu^\pi (s) \pi(a|s)}{\sum_{a'} \nu^\pi (s) \pi(a'|s)} \\
&= \frac{\rho^\pi (s,a)}{\sum_{a'} \rho^\pi (s,a')}. 
\end{align*}
$$

则给定$\rho$可以确定唯一的策略$\pi_\rho$.
