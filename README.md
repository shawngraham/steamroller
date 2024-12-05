I call this 'steamroller' because it's meant to take a towering edifice of unstructured text and flatten it into a knowledge graph. You define your list of predicates, and then run the pipeline. At the other end, you get a csv and a gexf file for further exploration and analysis.

The idea is that we remove ambiguity in the text by writing out personal names fully, removing citations if they exist, and then using coreference resolution to make it clear what actor is doing what. Then we use a language model to extract the triplets according to the template. The pipeline pauses after that and marks up which results don't conform to the desired list of predicates (or are not in triplet form). The user can make adjustments, then the pipeline resumes to do the final reshaping.

The results of each step are written to a new folder. The user might want to run the pipeline one step at a time, or perhaps skip a step. If you do skip a step, just make sure to adjust the code for the _next_ step so that it reads the correct folder. 

```
$ conda create -n steamroller python=3.11
$ conda activate steamroller
$ conda install -c conda-forge spacy=3.5.0
$ conda install -c conda-forge spacy-transformers
$ python -m spacy download en_core_web_trf=3.5.0
$ python -m spacy download en_core_web_lg
$ conda install -c conda-forge protobuf
$ conda install -c conda-forge sentencepiece
$ python -m pip install coreferee
$ python -m coreferee install en
$ pip install llm
$ pip install pandas
$ pip install networkx
```

...for whatever reason, all of those installs weren't working on my local machine using a requirements.txt file. Anywho. (Indeed, ultimately it turned out that I had an older version of conda that needed updating and fixing. Read those error messages carefully, folks.) 

Then, use llm [llm.datasette.io](https://llm.datasette.io) to set your model preference. You have to set an alias for whatever model you're going to use as 'themodel'. E.g:

```
llm install llm-groq
llm keys set groq
llm aliases set themodel groq-llama3.1-70b
llm -m themodel 'is this thing on'
```

Structure will be:

```
steamroller/
├── src/
│   ├── name_replacement.py
│   ├── citation_removal.py
│   ├── coref_resolution.py
│   ├── triplet_extraction.py
│   └── csv_processing.py
├── source-texts/  (Place your input .txt files here)
├── results/
│   └── step-one/
│   └── step-two/
│   └── step-three/
│   └── step-four/
│   └── step-five/
│   └── finished/
├── requirements.txt
└── run_pipeline.sh
```

You might need to `chmod +x run_pipeline.sh`

Then: `./run_pipeline.sh`


The coreference resolution was working wonderfully in google colab, but I'm having a devil of a time making it work locally. Your milage may vary.

Incidentally, I've commented out the citation removal step, and just piped the name_replacement to feed the coref, skipping citation removal (which is slightly borked I now discover. Sigh...)

graph TD
    A[Start] --> B{Create directories};
    B --> C[Run initial stages];
    C --> D[python src/name_replacement.py];
    D --> E[python src/coref_resolution.py];
    E --> F[python src/triplet_extraction.py];
    F --> G[Run error checking];
    G --> H[python src/csv_processing.py error_check];
    H --> I[Manual Inspection];
    I --> J{Manual checks complete?};
    J -- Yes --> K[Continue processing];
    J -- No --> I;
    K --> L[python src/csv_processing.py final_process];
    L --> M[python src/csv_processing.py concatenate];
    M --> N[python src/csv_processing.py gexf];
    N --> O[End];

    subgraph "Initial Stages"
        C --> D;
        D --> E;
        E --> F;
    end

    subgraph "Error Checking"
        G --> H;
    end

    subgraph "Final Processing"
        K --> L;
        L --> M;
        M --> N;
    end

    subgraph "name_replacement.py"
        D1[Read text files] --> D2[Extract full names];
        D2 --> D3[Replace surnames];
        D3 --> D4[Write to output];
    end

    subgraph "coref_resolution.py"
        E1[Read text files] --> E2[Process with spacy and coreferee];
        E2 --> E3[Perform entity co-resolution];
        E3 --> E4[Write to output];
    end

    subgraph "triplet_extraction.py"
        F1[Read text files] --> F2[Split into paragraphs];
        F2 --> F3[Send to LLM];
        F3 --> F4[Extract triplets];
        F4 --> F5[Write to CSV];
    end

    subgraph "csv_processing.py"
        H1[error_check] --> H2[Check predicates and column count];
        H2 --> H3[Write to output];
        L1[final_process] --> L2[Process CSVs];
        L2 --> L3[Write to output];
        M1[concatenate] --> M2[Combine CSVs];
        M2 --> M3[Write to output];
        N1[gexf] --> N2[Convert CSV to GEXF];
        N2 --> N3[Write to output];

    end
