# A candid introduction to Quantum Computing

These notes are organized as an interactive tutorial on the fundamentals of quantum computing. The pages here
are markdown conversions of interactive Jupyter notebooks that can be downloaded and executed on either your 
own computer or with [Google colab](https://colab.research.google.com/) (for example).


In full disclosure to the reader, I would like to put it on the record that <b>I am not an expert in this subject</b>. 
While I have spent a fair bit of time thinking about and digesting this content, I myself am relatively new to the area of quantum computation and information. That being said, the experiences of discovering effective explanations that clicked for me are still relatively fresh in my memory -- and my hope is to share some of that with the reader in this candid introduction to the subject. There are plenty of authoritative references to this material (for example, a classic is "Quantum Computation and Quantum Information" by Nielsen-Chuang), and I encourage anybody seeing this material for the first time to also consult a more authoritative source. My focus in writing these notes was more towards relatability and narrative.

This mini-course is roughly organized into 5 parts:

1. The first part will be focusing on general introductions, and exploring the information theoretic foundations underlying quantum computing

2. The second part will focus on Grover's search algorithm, after a few words on some more novel aspects of quantum algorithms (i.e. novel when compared to classical algorithms)

3. The third part will focus on the quantum Fourier transform and quantum phase estimation

4. The fourth part will feature one of the most famous quantum algorithms: Shor's algorithm. 

5. Finally, we will move onto quantum error correction for the fifth part of this mini-course. 


If you are running this code locally, you should head over to [ibm/qiskit](https://www.ibm.com/quantum/qiskit) and install qiskit. Otherwise, you can follow along or open up these notebooks in [Google colab](https://colab.research.google.com/). I believe that qiskit is readily available on Google colab and does not require any further downloading or installing. 

<!-- These notes are organized as an interactive textbook.

Use the sidebar to move between chapters. The notebook chapters are available here:

- [Part I: Introduction and Foundations](qc1.html)
- [Part II: Circuits and Algorithms, Grover Search](part-2.html)

You can add new chapters by creating Markdown files in `src/` and listing them in `src/SUMMARY.md`. -->
