# a template for coreference resolution using LLM

Run the following at the terminal:

```
llm --system """Perform coreference resolution on the $input, replacing all mentions of the same entity with a consistent unique identifier. RULES: 1 - Identify all pronouns referring to the same real-world entity. 2 - The first mention of an entity should retain its original descriptive text and be assigned for all subsequent mentions. 3 - Preserve the original text structure and context. 4 - Ensure replacements are consistent throughout the text. 5 - DO NOT ADD ANY OTHER TEXT. Examples: - Input: 'Emily Smith ran the Boston Marathon. She trained for months. The amazing marathoner completed the race.' Output: 'Emily Smith ran the Boston Marathon. Emily Smith trained for months. Emily Smith completed the Boston Marathon.' - Input: 'John Doe bought a car. The vehicle was red. He drove it to work.'Output: 'John Doe bought a car. The car was red. John Doe drove the car to work.' RETURN ONLY THE MODIFIED TEXT with coreference resolution applied.""" --save coresolver
```

Then, to use it,

```bash
cat /results/namefixed/39.txt | llm -m groq-llama3.1-70b -t coresolver
```

**original source-texts/39.txt:**

> Giacomo Medici started dealing in antiquities in Rome during the 1960s . In July 1967 , Giacomo Medici was convicted in Italy of receiving looted artefacts , though in the same year he met and became an important supplier of antiquities to US dealer Robert Hecht . In 1968 , Giacomo Medici opened the gallery Antiquaria Romana in Rome and began to explore business opportunities in Switzerland . It is widely believed that in December 1971 he bought the illegally - excavated Euphronios ( Sarpedon ) krater from tombaroli before transporting it to Switzerland and selling it to Robert Hecht . 
> In 1978 , he closed his Rome gallery , and entered into partnership with Geneva resident Christian Boursaud , who started consigning material supplied by Giacomo Medici for sale at Sotheby ’s London . Together , they opened Hydra Gallery in Geneva in 1983 . It has been estimated that throughout the 1980s Giacomo Medici was the source of more consignments to Sotheby ’s London than any other vendor . At any one time , Christian Boursaud might consign anything up to seventy objects , worth together as much as £ 500,000 . Material would be delivered to Sotheby ’s from Geneva by courier . 

**first two paragraphs from results/namefixed/39.txt:**

> Giacomo Medici started dealing in antiquities in Rome during the 1960s . In July 1967 , Giacomo Medici was convicted in Italy of receiving looted artefacts , though in the same year he met and became an important supplier of antiquities to US dealer Robert Hecht . In 1968 , Giacomo Medici opened the gallery Antiquaria Romana in Rome and began to explore business opportunities in Switzerland . It is widely believed that in December 1971 he bought the illegally - excavated Euphronios ( Sarpedon ) krater from tombaroli before transporting it to Switzerland and selling it to Robert Hecht . 
> In 1978 , he closed his Rome gallery , and entered into partnership with Geneva resident Christian Boursaud , who started consigning material supplied by Giacomo Medici for sale at Sotheby ’s London . Together , they opened Hydra Gallery in Geneva in 1983 . It has been estimated that throughout the 1980s Giacomo Medici was the source of more consignments to Sotheby ’s London than any other vendor . At any one time , Christian Boursaud might consign anything up to seventy objects , worth together as much as £ 500,000 . Material would be delivered to Sotheby ’s from Geneva by courier .

**After running through coresolver:**

> Giacomo Medici started dealing in antiquities in Rome during the 1960s . In July 1967 , Giacomo Medici was convicted in Italy of receiving looted artefacts , though in the same year Giacomo Medici met and became an important supplier of antiquities to US dealer Robert Hecht . In 1968 , Giacomo Medici opened the gallery Antiquaria Romana in Rome and began to explore business opportunities in Switzerland . It is widely believed that in December 1971 Giacomo Medici bought the illegally - excavated Euphronios ( Sarpedon ) krater from tombaroli before transporting it to Switzerland and selling it to Robert Hecht . 
> In 1978 , Giacomo Medici closed his Rome gallery , and entered into partnership with Geneva resident Christian Boursaud , who started consigning material supplied by Giacomo Medici for sale at Sotheby ’s London . Together , they opened Hydra Gallery in Geneva in 1983 . It has been estimated that throughout the 1980s Giacomo Medici was the source of more consignments to Sotheby ’s London than any other vendor . At any one time , Christian Boursaud might consign anything up to seventy objects , worth together as much as £ 500,000 . Material would be delivered to Sotheby ’s from Geneva by courier .
>
> 
