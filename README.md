<div align="center">
  <img src="https://github.com/C4dynamics/C4dynamics/blob/main/tools/C4dynamics.png">
</div>

#### Tsipor Dynamics
#### Algorithms Engineering and Development
****

C4Dynamics (read Tsipor (bird) Dynamics) is an open-source framework for algorithms engineering! 


[![My Skills](https://skillicons.dev/icons?i=python)](https://skillicons.dev)


Welcome to C4dynamics - an open-source framework for algorithm engineers who work with physical and dynamical systems. 


This framework is designed to help algorithm engineers quickly and efficiently implement and test new algorithms. 

It includes a variety of tools and features to streamline the development process, including:

✅ A comprehensive library of common algorithms and data structures!

* Data-point and rigid-body objects

* 6DOF (six degrees of freedom) simulation

* Seekers and sensors

* Save and plot state-vector in one klick

✅ A robust testing suite to ensure the reliability and correctness of your implementation!

✅ An intuitive API for easily integrating your algorithms into larger systems!

✅ Documentation and examples to help you get up and running quickly!



Whether you're a seasoned algorithm engineer or just getting started, this framework has something to offer. Its modular design allows you to easily pick and choose the components you need, and its active community of contributors is always working to improve and expand its capabilities.

So why wait? Start using the C4dynamics today and take your algorithms engineering to the next level!

## Note
This frameworked is aimed mainly for the purpose of developing algorithms for physical and dynamical systems: predicting and controlling motion. 

## Quickstart

See jupyter notebook demonstrations in examples (GitHub repository). 

Install the required packages:
```
pip install -r requirements.txt
```

Define radar with C4dynamics: 

```
import C4dynamics as c4d
rdr = c4d.seekers.dzradar([0, 0, 0], c4d.filters.filtertype.ex_kalman, 50e-3)
```

Define moving target with C4dynamics: 

```
import C4dynamics as c4d
tgt = c4d.datapoint(x = 1000, vx = 100)
```

Define errors to a general-purpose seeker with C4dynamics: 

```
import C4dynamics as c4d
rdr = c4d.seekers.radar(sf = 0.9, bias = 0, noisestd = 1)
```


# Quickstart for Contributors

* Press the 'Fork' button (upper right corner of the C4dynamics page)
* Clone C4dynamics to your local machine (GitHub Desktop is a nice tool to help you clone and push your changes back)
* Create a new python notebook 
* Import C4dynamics to your notebook (see some examples in the repository 'examples')
* In the notebook, write some code you would like to do using the C4dynamics library
* Create and edit files in C4dynamics to support your code
* Make tests and document your changes
* Push the changes back to your GitHub
* Press the 'Pull Request' button. Submit a message with details about your changes.


## Contributors ✨


<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>	
      <td align="center"><a href="https://github.com/C4dynamics"><img src="https://github.com/C4dynamics/C4dynamics/blob/main/tools/ziv_noa.jpg" width="100px;" alt="Ziv Meri"/> <br /><sub><b>Ziv Meri</b></sub></a><br /><a href="https://github.com/C4dynamics" title="Code">💻</a></td>
      <td align="center"><a href="https://chat.openai.com/chat"><img src="https://github.com/C4dynamics/C4dynamics/blob/main/tools/openai-featured.png" width="100px;"/> <br /><sub><b>Chat GPT</b></sub></a><br /><a href="https://chat.openai.com/chat" title="Support">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

