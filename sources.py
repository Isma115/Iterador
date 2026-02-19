# sources.py

TRUSTED_SOURCES = [
    # --- Fuentes Generales y de Referencia (Internacional) ---
    {"name": "Wolfram Alpha", "domain": "wolframalpha.com"},
    {"name": "Encyclopedia Britannica", "domain": "britannica.com"},
    {"name": "Wikipedia (Revisada/Español)", "domain": "es.wikipedia.org"}, # Often useful for overview
    
    # --- Ciencia, Investigación y Académico (Español/LatAm) ---
    {"name": "Scielo (Scientific Electronic Library Online)", "domain": "scielo.org"},
    {"name": "Dialnet (Universidad de La Rioja)", "domain": "dialnet.unirioja.es"},
    {"name": "Redalyc", "domain": "redalyc.org"},
    {"name": "CSIC (España)", "domain": "csic.es"},
    {"name": "Digital.CSIC", "domain": "digital.csic.es"},
    {"name": "Biblioteca Virtual Miguel de Cervantes", "domain": "cervantesvirtual.com"},
    {"name": "RAE (Real Academia Española)", "domain": "rae.es"},
    {"name": "Latindex", "domain": "latindex.org"},
    {"name": "Biblioteca Nacional de España", "domain": "bne.es"},
    {"name": "Biblioteca Digital Hispánica", "domain": "bdh.bne.es"},
    {"name": "FECYT (Ciencia y Tecnología)", "domain": "fecyt.es"},
    
    # --- Universidades Prestigiosas (Habla Hispana) ---
    {"name": "UNAM (México)", "domain": "unam.mx"},
    {"name": "Tecnológico de Monterrey", "domain": "tec.mx"},
    {"name": "Universidad de Buenos Aires (UBA)", "domain": "uba.ar"},
    {"name": "Universidad de Chile", "domain": "uchile.cl"},
    {"name": "Pontificia Universidad Católica de Chile", "domain": "uc.cl"},
    {"name": "Universidad de los Andes (Colombia)", "domain": "uniandes.edu.co"},
    {"name": "Universitat de Barcelona", "domain": "ub.edu"},
    {"name": "Universidad Autónoma de Madrid", "domain": "uam.es"},
    {"name": "Universidad Complutense de Madrid", "domain": "ucm.es"},
    
    # --- Salud y Medicina (Español) ---
    {"name": "Organización Mundial de la Salud (OMS)", "domain": "who.int/es"},
    {"name": "OPS (Organización Panamericana de la Salud)", "domain": "paho.org"},
    {"name": "NIH en español", "domain": "salud.nih.gov"},
    {"name": "MedlinePlus Español", "domain": "medlineplus.gov/spanish"},
    {"name": "Mayo Clinic Español", "domain": "mayoclinic.org/es"},
    {"name": "MSD Manuals Español", "domain": "msdmanuals.com/es"},
    {"name": "Cochrane Iberoamérica", "domain": "es.cochrane.org"},
    {"name": "AEMPS (Medicamentos España)", "domain": "aemps.gob.es"},
    {"name": "Instituto de Salud Carlos III", "domain": "isciii.es"},
    {"name": "Salud sin Bulos", "domain": "saludsinbulos.com"},
    
    # --- Ciencia e Investigación (Internacional - Inglés/Español) ---
    {"name": "Google Scholar", "domain": "scholar.google.com"},
    {"name": "PubMed", "domain": "pubmed.ncbi.nlm.nih.gov"},
    {"name": "ScienceDirect", "domain": "sciencedirect.com"},
    {"name": "NASA en español", "domain": "ciencia.nasa.gov"},
    {"name": "NASA (English)", "domain": "nasa.gov"},
    {"name": "ESA (Agencia Espacial Europea)", "domain": "esa.int"},
    {"name": "Nature", "domain": "nature.com"},
    {"name": "Science Magazine", "domain": "science.org"},
    {"name": "PLOS One", "domain": "journals.plos.org"},
    {"name": "DOAJ (Directory of Open Access Journals)", "domain": "doaj.org"},
    {"name": "arXiv", "domain": "arxiv.org"},
    {"name": "JSTOR", "domain": "jstor.org"},
    {"name": "ResearchGate", "domain": "researchgate.net"},
    {"name": "IEEE Xplore", "domain": "ieeexplore.ieee.org"},
    
    # --- Noticias y Actualidad Rigurosa (Español) ---
    {"name": "Agencia SINC (Noticias Científicas)", "domain": "agenciasinc.es"},
    {"name": "The Conversation (España)", "domain": "theconversation.com/es"},
    {"name": "El País - Ciencia/Materia", "domain": "elpais.com/ciencia"},
    {"name": "BBC Mundo", "domain": "bbc.com/mundo"},
    {"name": "DW Español (Deutsche Welle)", "domain": "dw.com/es"},
    {"name": "Euronews", "domain": "euronews.com"},
    {"name": "EFE", "domain": "efe.com"},
    {"name": "Europa Press", "domain": "europapress.es"},
    {"name": "National Geographic España", "domain": "nationalgeographic.com.es"},
    {"name": "Maldita.es (Fact Checking)", "domain": "maldita.es"},
    {"name": "Newtral", "domain": "newtral.es"},
    {"name": "Fundación BBVA", "domain": "fbbva.es"},
    
    # --- Organismos Internacionales (Español) ---
    {"name": "Naciones Unidas (ONU)", "domain": "un.org/es"},
    {"name": "UNESCO", "domain": "unesco.org/es"},
    {"name": "FAO", "domain": "fao.org/es"},
    {"name": "Banco Mundial", "domain": "bancomundial.org"},
    {"name": "FMI (Fondo Monetario Internacional)", "domain": "imf.org/es"},
    {"name": "CEPAL", "domain": "cepal.org"},
    {"name": "Statista", "domain": "es.statista.com"},
    
    # --- Tecnología y Programación ---
    {"name": "MDN Web Docs", "domain": "developer.mozilla.org"},
    {"name": "Stack Overflow (es)", "domain": "es.stackoverflow.com"},
    {"name": "Stack Overflow (en)", "domain": "stackoverflow.com"},
    {"name": "Python Docs", "domain": "docs.python.org"},
    {"name": "W3C", "domain": "w3.org"},
    {"name": "Microsoft Learn", "domain": "learn.microsoft.com"},

    # --- Psicología y Ciencias Sociales ---
    {"name": "APA (American Psychological Association)", "domain": "apa.org"},
    {"name": "Psychology Today (Verificado)", "domain": "psychologytoday.com"},
    {"name": "Scientific American (Mente)", "domain": "scientificamerican.com/mind"},
    {"name": "Simply Psychology", "domain": "simplypsychology.org"},
    
    # --- Economía, Derecho y Estadística (Datos Oficiales) ---
    {"name": "INE (Instituto Nacional de Estadística - España)", "domain": "ine.es"},
    {"name": "Eurostat", "domain": "ec.europa.eu/eurostat"},
    {"name": "BOE (Boletín Oficial del Estado)", "domain": "boe.es"},
    {"name": "Eur-Lex (Derecho UE)", "domain": "eur-lex.europa.eu"},
    {"name": "Banco de España", "domain": "bde.es"},
    {"name": "OECD (OCDE)", "domain": "oecd.org"},
    
    # --- Educación y Tecnología Educativa ---
    {"name": "Edutopia", "domain": "edutopia.org"},
    {"name": "Khan Academy", "domain": "khanacademy.org"},
    {"name": "Coursera Blog", "domain": "blog.coursera.org"},
    {"name": "MIT OpenCourseWare", "domain": "ocw.mit.edu"},
    
    # --- Medio Ambiente y Naturaleza ---
    {"name": "National Geographic", "domain": "nationalgeographic.com"},
    {"name": "EPA (Agencia Protección Ambiental EEUU)", "domain": "epa.gov"},
    {"name": "MITECO (Ministerio Transición Ecológica España)", "domain": "miteco.gob.es"},
    
    # --- Universidades Top Mundial (Inglés) ---
    {"name": "Harvard University", "domain": "harvard.edu"},
    {"name": "MIT (Massachusetts Institute of Technology)", "domain": "mit.edu"},
    {"name": "Stanford University", "domain": "stanford.edu"},
    {"name": "University of Oxford", "domain": "ox.ac.uk"},
    {"name": "University of Cambridge", "domain": "cam.ac.uk"},
    {"name": "Berkeley (University of California)", "domain": "berkeley.edu"},
    {"name": "Princeton University", "domain": "princeton.edu"},
    {"name": "Yale University", "domain": "yale.edu"},
    {"name": "Caltech", "domain": "caltech.edu"}
]
