from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://dbpedia.org/sparql",
                       returnFormat=JSON)
sparql.setQuery("""
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?actor ?name WHERE {
        ?tvshow rdf:type dbo:TelevisionShow.
        ?tvshow rdfs:label "Friends"@en.
        ?tvshow dbo:starring ?actor.
        ?actor foaf:name ?name
    }
""")
results = sparql.query().convert()

for result in results["results"]["bindings"]:
    print(result["actor"]["value"], result["name"]["value"])
