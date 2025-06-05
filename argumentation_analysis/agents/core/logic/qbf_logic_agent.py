# argumentation_analysis/agents/core/logic/qbf_logic_agent.py
"""
Agent spécialisé pour la logique des formules booléennes quantifiées (QBF).

Ce module définit `QBFLogicAgent`, une classe qui hérite de
`BaseLogicAgent` et implémente les fonctionnalités spécifiques pour interagir
avec la logique QBF. Il utilise `TweetyBridge` pour la communication
avec TweetyProject et s'appuie sur des prompts sémantiques définis dans ce
module pour la conversion texte-vers-QBF, la génération de requêtes et
l'interprétation des résultats.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple

from semantic_kernel import Kernel

from ..abc.agent_bases import BaseLogicAgent
from .belief_set import BeliefSet, QBFBeliefSet
from .tweety_bridge import TweetyBridge

# Configuration du logger
logger = logging.getLogger(__name__)

# Prompt Système pour l'agent QBF
SYSTEM_PROMPT_QBF = """Vous êtes un agent spécialisé dans l'analyse et le raisonnement en logique des formules booléennes quantifiées (QBF).
Vous utilisez la syntaxe de TweetyProject pour représenter les formules QBF.
Vos tâches principales incluent la traduction de texte en formules QBF, la génération de requêtes QBF pertinentes,
l'exécution de ces requêtes sur un ensemble de croyances QBF, et l'interprétation des résultats obtenus,
en tenant compte des quantificateurs existentiels et universels sur les variables booléennes.
"""

# Prompts pour la logique QBF
PROMPT_TEXT_TO_QBF = """
Vous êtes un expert en logique des formules booléennes quantifiées (QBF). Votre tâche est de traduire un texte en un ensemble de croyances (belief set) en logique QBF en utilisant la syntaxe de TweetyProject.

Syntaxe de la logique QBF pour TweetyProject:
- Variables booléennes: lettres minuscules (ex: x, y, z)
- Connecteurs logiques: !, ||, &&, =>, <=>
- Quantificateurs: exists x (formule), forall x (formule)
  - exists x signifie "il existe x tel que"
  - forall x signifie "pour tout x"

Règles importantes:
1. Chaque formule doit se terminer par un point-virgule (;) 
2. Les formules sont séparées par des sauts de ligne
3. Utilisez des noms significatifs pour les variables
4. Évitez les espaces dans les noms des variables
5. Les commentaires commencent par % et s'étendent jusqu'à la fin de la ligne
6. Vous pouvez imbriquer les quantificateurs: exists x forall y (formule)

Exemple:
```
% Exemple de formules QBF
exists x (x);
forall y (y => y);
exists x forall y (x || !y);
forall a exists b (a => b);
```

Traduisez maintenant le texte suivant en un ensemble de croyances en logique QBF:

{{$input}}

Répondez uniquement avec l'ensemble de croyances en logique QBF, sans explications supplémentaires.
"""

PROMPT_GEN_QBF_QUERIES = """
Vous êtes un expert en logique QBF. Votre tâche est de générer des requêtes pertinentes en logique QBF pour interroger un ensemble de croyances (belief set) donné.

Voici le texte source:
{{$input}}

Voici l'ensemble de croyances en logique QBF:
{{$belief_set}}

Générez 3 à 5 requêtes pertinentes en logique QBF qui permettraient de vérifier des implications importantes ou des conclusions intéressantes à partir de cet ensemble de croyances. Utilisez la même syntaxe que celle de l'ensemble de croyances.

Règles importantes:
1. Les requêtes doivent être des formules bien formées en logique QBF
2. Utilisez uniquement des variables déjà définies dans l'ensemble de croyances
3. Chaque requête doit être sur une ligne séparée
4. N'incluez pas de point-virgule à la fin des requêtes
5. Assurez-vous que les requêtes sont pertinentes par rapport au texte source
6. Utilisez les quantificateurs exists et forall de manière appropriée

Répondez uniquement avec les requêtes, sans explications supplémentaires.
"""

PROMPT_INTERPRET_QBF = """
Vous êtes un expert en logique QBF. Votre tâche est d'interpréter les résultats de requêtes en logique QBF et d'expliquer leur signification dans le contexte du texte source.

Voici le texte source:
{{$input}}

Voici l'ensemble de croyances en logique QBF:
{{$belief_set}}

Voici les requêtes qui ont été exécutées:
{{$queries}}

Voici les résultats de ces requêtes:
{{$tweety_result}}

Interprétez ces résultats et expliquez leur signification dans le contexte du texte source. Pour chaque requête:
1. Expliquez ce que la requête cherchait à vérifier
2. Indiquez si la requête a été acceptée (ACCEPTED) ou rejetée (REJECTED)
3. Expliquez ce que cela signifie dans le contexte du texte source
4. Si pertinent, mentionnez les implications logiques de ce résultat concernant la satisfiabilité et les quantificateurs

Fournissez ensuite une conclusion générale sur ce que ces résultats nous apprennent sur le texte source, en particulier concernant l'existence de solutions et la validité universelle des propriétés.

Votre réponse doit être claire, précise et accessible à quelqu'un qui n'est pas expert en logique formelle.
"""


class QBFLogicAgent(BaseLogicAgent):
    """
    Agent spécialisé pour la logique des formules booléennes quantifiées (QBF).

    Cet agent étend `BaseLogicAgent` pour fournir des capacités de traitement
    spécifiques à la logique QBF. Il intègre des fonctions sémantiques
    pour traduire le langage naturel en ensembles de croyances QBF, générer des
    requêtes QBF pertinentes, exécuter ces requêtes via `TweetyBridge`, et
    interpréter les résultats en langage naturel.

    Attributes:
        _tweety_bridge (TweetyBridge): Instance de `TweetyBridge` configurée pour la QBF.
    """
    
    def __init__(self, kernel: Kernel):
        """
        Initialise une instance de `QBFLogicAgent`.

        :param kernel: Le kernel Semantic Kernel à utiliser pour les fonctions sémantiques.
        :type kernel: Kernel
        """
        super().__init__(kernel,
                         agent_name="QBFLogicAgent",
                         logic_type_name="QBF",
                         system_prompt=SYSTEM_PROMPT_QBF)

    def get_agent_capabilities(self) -> Dict[str, Any]:
        """
        Retourne un dictionnaire décrivant les capacités spécifiques de cet agent QBF.

        :return: Un dictionnaire détaillant le nom, le type de logique, la description
                 et les méthodes de l'agent.
        :rtype: Dict[str, Any]
        """
        return {
            "name": self.name,
            "logic_type": self.logic_type,
            "description": "Agent capable d'analyser du texte en utilisant la logique des formules booléennes quantifiées (QBF). "
                           "Peut convertir du texte en un ensemble de croyances QBF, générer des requêtes QBF, "
                           "exécuter ces requêtes, et interpréter les résultats en termes de satisfiabilité quantifiée.",
            "methods": {
                "text_to_belief_set": "Convertit un texte en un ensemble de croyances QBF.",
                "generate_queries": "Génère des requêtes QBF pertinentes à partir d'un texte et d'un ensemble de croyances.",
                "execute_query": "Exécute une requête QBF sur un ensemble de croyances.",
                "interpret_results": "Interprète les résultats d'une ou plusieurs requêtes QBF.",
                "validate_formula": "Valide la syntaxe d'une formule QBF."
            }
        }

    def setup_agent_components(self, llm_service_id: str) -> None:
        """
        Configure les composants spécifiques de l'agent de logique QBF.

        Initialise `TweetyBridge` pour la logique QBF et enregistre les fonctions
        sémantiques nécessaires dans le kernel Semantic Kernel.

        :param llm_service_id: L'ID du service LLM à utiliser pour les fonctions sémantiques.
        :type llm_service_id: str
        """
        super().setup_agent_components(llm_service_id)
        self.logger.info(f"Configuration des composants pour {self.name}...")

        self._tweety_bridge = TweetyBridge()

        if not self.tweety_bridge.is_jvm_ready():
            self.logger.error("Tentative de setup QBF Kernel alors que la JVM n'est PAS démarrée.")
            return
        
        default_settings = None
        if self._llm_service_id:
            try:
                default_settings = self.sk_kernel.get_prompt_execution_settings_from_service_id(
                    self._llm_service_id
                )
                self.logger.debug(f"Settings LLM récupérés pour {self.name}.")
            except Exception as e:
                self.logger.warning(f"Impossible de récupérer settings LLM pour {self.name}: {e}")

        semantic_functions = [
            ("TextToQBFBeliefSet", PROMPT_TEXT_TO_QBF,
             "Traduit texte en Belief Set QBF (syntaxe Tweety pour logique QBF)."),
            ("GenerateQBFQueries", PROMPT_GEN_QBF_QUERIES,
             "Génère requêtes QBF pertinentes (syntaxe Tweety pour logique QBF)."),
            ("InterpretQBFResult", PROMPT_INTERPRET_QBF,
             "Interprète résultat requête QBF Tweety formaté.")
        ]

        for func_name, prompt, description in semantic_functions:
            try:
                if not prompt or not isinstance(prompt, str):
                    self.logger.error(f"ERREUR: Prompt invalide pour {self.name}.{func_name}")
                    continue
                
                self.logger.info(f"Ajout fonction {self.name}.{func_name} avec prompt de {len(prompt)} caractères")
                self.sk_kernel.add_function(
                    prompt=prompt,
                    plugin_name=self.name,
                    function_name=func_name,
                    description=description,
                    prompt_execution_settings=default_settings
                )
                self.logger.debug(f"Fonction sémantique {self.name}.{func_name} ajoutée/mise à jour.")
                
                if self.name in self.sk_kernel.plugins and func_name in self.sk_kernel.plugins[self.name]:
                    self.logger.info(f"✅ Fonction {self.name}.{func_name} correctement enregistrée.")
                else:
                    self.logger.error(f"❌ ERREUR CRITIQUE: Fonction {self.name}.{func_name} non trouvée après ajout!")
            except ValueError as ve:
                self.logger.warning(f"Problème ajout/MàJ {self.name}.{func_name}: {ve}")
            except Exception as e:
                self.logger.error(f"Exception inattendue lors de l'ajout de {self.name}.{func_name}: {e}", exc_info=True)
        
        self.logger.info(f"Composants de {self.name} configurés.")

    async def text_to_belief_set(self, text: str, context: Optional[Dict[str, Any]] = None) -> Tuple[Optional[BeliefSet], str]:
        """
        Convertit un texte en langage naturel en un ensemble de croyances QBF.

        Utilise la fonction sémantique "TextToQBFBeliefSet" pour la conversion,
        puis valide l'ensemble de croyances généré avec `TweetyBridge`.

        :param text: Le texte en langage naturel à convertir.
        :type text: str
        :param context: Un dictionnaire optionnel de contexte (non utilisé actuellement).
        :type context: Optional[Dict[str, Any]]
        :return: Un tuple contenant l'objet `QBFBeliefSet` si la conversion
                 et la validation réussissent, et un message de statut.
                 Retourne (None, message_erreur) en cas d'échec.
        :rtype: Tuple[Optional[BeliefSet], str]
        """
        self.logger.info(f"Conversion de texte en ensemble de croyances QBF pour l'agent {self.name}...")
        
        try:
            result = await self.sk_kernel.plugins[self.name]["TextToQBFBeliefSet"].invoke(self.sk_kernel, input=text)
            belief_set_content = str(result)
            
            if not belief_set_content or len(belief_set_content.strip()) == 0:
                self.logger.error("La conversion a produit un ensemble de croyances vide")
                return None, "La conversion a produit un ensemble de croyances vide"
            
            belief_set_obj = QBFBeliefSet(belief_set_content)
            
            is_valid, validation_msg = self.tweety_bridge.validate_qbf_belief_set(belief_set_content)
            if not is_valid:
                self.logger.error(f"Ensemble de croyances invalide: {validation_msg}")
                return None, f"Ensemble de croyances invalide: {validation_msg}"
            
            self.logger.info("Conversion réussie")
            return belief_set_obj, "Conversion réussie"
        
        except Exception as e:
            error_msg = f"Erreur lors de la conversion du texte en ensemble de croyances: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return None, error_msg
    
    async def generate_queries(self, text: str, belief_set: BeliefSet, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Génère des requêtes logiques QBF pertinentes à partir d'un texte et d'un ensemble de croyances.

        Utilise la fonction sémantique "GenerateQBFQueries". Les requêtes générées
        sont ensuite validées syntaxiquement.

        :param text: Le texte en langage naturel source.
        :type text: str
        :param belief_set: L'ensemble de croyances QBF associé.
        :type belief_set: BeliefSet
        :param context: Un dictionnaire optionnel de contexte (non utilisé actuellement).
        :type context: Optional[Dict[str, Any]]
        :return: Une liste de chaînes de caractères, chacune étant une requête QBF valide.
                 Retourne une liste vide en cas d'erreur.
        :rtype: List[str]
        """
        self.logger.info(f"Génération de requêtes QBF pour l'agent {self.name}...")
        
        try:
            result = await self.sk_kernel.plugins[self.name]["GenerateQBFQueries"].invoke(
                self.sk_kernel,
                input=text,
                belief_set=belief_set.content
            )
            queries_text = str(result)
            
            queries = [q.strip() for q in queries_text.split('\n') if q.strip()]
            
            valid_queries = []
            for query_item in queries:
                is_valid, _ = self.tweety_bridge.validate_qbf_formula(query_item)
                if is_valid:
                    valid_queries.append(query_item)
                else:
                    self.logger.warning(f"Requête invalide ignorée: {query_item}")
            
            self.logger.info(f"Génération de {len(valid_queries)} requêtes valides")
            return valid_queries
        
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération des requêtes: {str(e)}", exc_info=True)
            return []
    
    def execute_query(self, belief_set: BeliefSet, query: str) -> Tuple[Optional[bool], str]:
        """
        Exécute une requête logique QBF sur un ensemble de croyances donné.

        Utilise `TweetyBridge` pour exécuter la requête contre le contenu de `belief_set`.
        Interprète la chaîne de résultat de `TweetyBridge` pour déterminer si la requête
        est acceptée, rejetée ou si une erreur s'est produite.

        :param belief_set: L'ensemble de croyances QBF sur lequel exécuter la requête.
        :type belief_set: BeliefSet
        :param query: La requête QBF à exécuter.
        :type query: str
        :return: Un tuple contenant le résultat booléen de la requête (`True` si acceptée,
                 `False` si rejetée, `None` si indéterminé ou erreur) et la chaîne de
                 résultat brute de `TweetyBridge` (ou un message d'erreur).
        :rtype: Tuple[Optional[bool], str]
        """
        self.logger.info(f"Exécution de la requête: {query} pour l'agent {self.name}")
        
        try:
            result_str = self.tweety_bridge.execute_qbf_query(
                belief_set_content=belief_set.content,
                query_string=query
            )
            
            if result_str is None or "ERROR" in result_str.upper():
                self.logger.error(f"Erreur lors de l'exécution de la requête: {result_str}")
                return None, result_str if result_str else "Erreur inconnue de TweetyBridge"
            
            if "ACCEPTED" in result_str:
                return True, result_str
            elif "REJECTED" in result_str:
                return False, result_str
            else:
                self.logger.warning(f"Résultat de requête inattendu: {result_str}")
                return None, result_str
        
        except Exception as e:
            error_msg = f"Erreur lors de l'exécution de la requête: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return None, f"FUNC_ERROR: {error_msg}"

    async def interpret_results(self, text: str, belief_set: BeliefSet,
                         queries: List[str], results: List[Tuple[Optional[bool], str]],
                         context: Optional[Dict[str, Any]] = None) -> str:
        """
        Interprète les résultats d'une série de requêtes QBF en langage naturel.

        Utilise la fonction sémantique "InterpretQBFResult" pour générer une explication
        basée sur le texte original, l'ensemble de croyances, les requêtes posées et
        les résultats obtenus de Tweety.

        :param text: Le texte original en langage naturel.
        :type text: str
        :param belief_set: L'ensemble de croyances QBF utilisé.
        :type belief_set: BeliefSet
        :param queries: La liste des requêtes QBF qui ont été exécutées.
        :type queries: List[str]
        :param results: La liste des résultats (tuples booléen/None, message_brut)
                        correspondant à chaque requête.
        :type results: List[Tuple[Optional[bool], str]]
        :param context: Un dictionnaire optionnel de contexte (non utilisé actuellement).
        :type context: Optional[Dict[str, Any]]
        :return: Une chaîne de caractères contenant l'interprétation en langage naturel
                 des résultats, ou un message d'erreur.
        :rtype: str
        """
        self.logger.info(f"Interprétation des résultats pour l'agent {self.name}...")
        
        try:
            queries_str = "\n".join(queries)
            results_text_list = [res_tuple[1] if res_tuple else "Error: No result" for res_tuple in results]
            results_str = "\n".join(results_text_list)
            
            result = await self.sk_kernel.plugins[self.name]["InterpretQBFResult"].invoke(
                self.sk_kernel,
                input=text,
                belief_set=belief_set.content,
                queries=queries_str,
                tweety_result=results_str
            )
            
            interpretation = str(result)
            self.logger.info("Interprétation terminée")
            return interpretation
        
        except Exception as e:
            error_msg = f"Erreur lors de l'interprétation des résultats: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return f"Erreur d'interprétation: {error_msg}"

    def validate_formula(self, formula: str) -> bool:
        """
        Valide la syntaxe d'une formule QBF.

        Utilise la méthode `validate_qbf_formula` de `TweetyBridge`.

        :param formula: La formule QBF à valider.
        :type formula: str
        :return: `True` si la formule est syntaxiquement valide, `False` sinon.
        :rtype: bool
        """
        self.logger.debug(f"Validation de la formule QBF: {formula}")
        is_valid, message = self.tweety_bridge.validate_qbf_formula(formula)
        if not is_valid:
            self.logger.warning(f"Formule QBF invalide: {formula}. Message: {message}")
        return is_valid

    def _create_belief_set_from_data(self, belief_set_data: Dict[str, Any]) -> BeliefSet:
        """
        Crée un objet `QBFBeliefSet` à partir d'un dictionnaire de données.

        Principalement utilisé pour reconstituer un `BeliefSet` à partir d'un état sauvegardé.

        :param belief_set_data: Un dictionnaire contenant au moins la clé "content"
                                avec la représentation textuelle de l'ensemble de croyances.
        :type belief_set_data: Dict[str, Any]
        :return: Une instance de `QBFBeliefSet`.
        :rtype: BeliefSet
        """
        content = belief_set_data.get("content", "")
        return QBFBeliefSet(content)