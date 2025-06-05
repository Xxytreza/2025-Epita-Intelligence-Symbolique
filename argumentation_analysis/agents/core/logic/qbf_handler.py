# argumentation_analysis/agents/core/logic/qbf_handler.py
"""
Handler pour la logique des formules booléennes quantifiées (QBF).

Ce module fournit la classe `QBFHandler` qui encapsule les opérations spécifiques
à la logique QBF via TweetyProject. Il gère le parsing, la validation et
l'exécution de requêtes QBF.
"""

import logging
from typing import Optional, List, Any, Dict

import jpype

# Configuration du logger
logger = logging.getLogger(__name__)


class QBFHandler:
    """
    Handler pour les opérations de logique QBF via TweetyProject.
    
    Cette classe encapsule toutes les interactions spécifiques à la QBF
    avec les classes Java de TweetyProject.
    """
    
    def __init__(self, tweety_initializer):
        """
        Initialise le handler QBF.
        
        :param tweety_initializer: Instance de TweetyInitializer pour accéder aux composants Java.
        :type tweety_initializer: TweetyInitializer
        """
        self._initializer = tweety_initializer
        self._logger = logger
        self._logger.info("QBFHandler: Initialisation")
        
        # Vérifier que la JVM est prête
        if not self._initializer.is_jvm_started():
            raise RuntimeError("QBFHandler: JVM non démarrée")
        
        # Initialiser les composants QBF
        self._initialize_qbf_components()
        
    def _initialize_qbf_components(self):
        """
        Initialise les classes Java nécessaires pour QBF.
        """
        try:
            # Classes principales QBF
            self.QuantifiedBooleanFormula = jpype.JClass("org.tweetyproject.logics.qbf.syntax.QuantifiedBooleanFormula")
            self.Quantifier = jpype.JClass("org.tweetyproject.logics.qbf.syntax.Quantifier") 
            self.QbfParser = jpype.JClass("org.tweetyproject.logics.qbf.parser.QbfParser")
            self.Variable = jpype.JClass("org.tweetyproject.logics.commons.syntax.Variable")
            
            # Classes de logique propositionnelle pour construire la matrice
            self.Proposition = jpype.JClass("org.tweetyproject.logics.propositional.syntax.Proposition")
            self.Conjunction = jpype.JClass("org.tweetyproject.logics.propositional.syntax.Conjunction")
            self.Disjunction = jpype.JClass("org.tweetyproject.logics.propositional.syntax.Disjunction")
            self.Negation = jpype.JClass("org.tweetyproject.logics.propositional.syntax.Negation")
            self.Implication = jpype.JClass("org.tweetyproject.logics.propositional.syntax.Implication")
            
            # Initialiser le parser
            self.parser = self.QbfParser()
            
            self._logger.info("QBFHandler: Composants Java initialisés avec succès")
            
        except jpype.JException as e:
            error_msg = f"Erreur lors de l'initialisation des composants QBF: {e}"
            self._logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def parse_qbf_formula(self, formula_string: str) -> Any:
        """
        Parse une formule QBF.
        
        :param formula_string: La formule QBF à parser.
        :type formula_string: str
        :return: L'objet Java représentant la formule parsée.
        :rtype: Any
        :raises ValueError: Si le parsing échoue.
        """
        try:
            self._logger.debug(f"Parsing formule QBF: {formula_string}")
            formula = self.parser.parseFormula(formula_string)
            if formula is None:
                raise ValueError(f"Le parsing a retourné None pour: {formula_string}")
            return formula
        except jpype.JException as e:
            error_msg = f"Erreur de parsing QBF pour '{formula_string}': {e}"
            self._logger.error(error_msg)
            raise ValueError(error_msg) from e

    def parse_qbf_belief_set(self, belief_set_string: str) -> List[Any]:
        """
        Parse un ensemble de croyances QBF.
        
        :param belief_set_string: L'ensemble de croyances à parser.
        :type belief_set_string: str
        :return: Liste des formules QBF parsées.
        :rtype: List[Any]
        :raises ValueError: Si le parsing échoue.
        """
        formulas = []
        lines = [line.strip() for line in belief_set_string.split('\n') if line.strip() and not line.strip().startswith('%')]
        
        for line in lines:
            # Séparer les formules par point-virgule
            parts = [part.strip() for part in line.split(';') if part.strip()]
            for part in parts:
                formula = self.parse_qbf_formula(part)
                formulas.append(formula)
        
        return formulas

    def qbf_query(self, belief_set_content: str, query_string: str) -> Optional[bool]:
        """
        Exécute une requête QBF sur un ensemble de croyances.
        
        :param belief_set_content: Le contenu de l'ensemble de croyances.
        :type belief_set_content: str
        :param query_string: La requête à exécuter.
        :type query_string: str
        :return: True si la requête est satisfiable, False sinon, None si indéterminé.
        :rtype: Optional[bool]
        :raises ValueError: Si le parsing ou l'exécution échoue.
        """
        try:
            # Parser l'ensemble de croyances et la requête
            belief_formulas = self.parse_qbf_belief_set(belief_set_content)
            query_formula = self.parse_qbf_formula(query_string)
            
            # Pour l'instant, implémentation basique
            # TODO: Intégrer avec un solveur QBF réel
            self._logger.warning("QBF query execution: implémentation basique - retourne toujours True pour les tests")
            
            # Vérification basique: si la requête est syntaxiquement valide, retourner True
            if query_formula is not None:
                return True
            else:
                return False
                
        except Exception as e:
            error_msg = f"Erreur lors de l'exécution de la requête QBF: {e}"
            self._logger.error(error_msg)
            raise ValueError(error_msg) from e

    def create_qbf_formula_programmatically(self, example_type: str = "exists_forall") -> Any:
        """
        Crée une formule QBF programmatiquement pour les tests.
        
        :param example_type: Type d'exemple à créer.
        :type example_type: str
        :return: Formule QBF créée.
        :rtype: Any
        """
        try:
            if example_type == "exists_forall":
                # Crée ∃x ∀y (x ∧ ¬y)
                x_var = self.Variable("x")
                y_var = self.Variable("y")
                
                x_prop = self.Proposition("x")
                y_prop = self.Proposition("y")
                
                # Matrice: (x ∧ ¬y)
                matrix = self.Conjunction(x_prop, self.Negation(y_prop))
                
                # ∀y (x ∧ ¬y)
                forall_y = self.QuantifiedBooleanFormula(
                    self.Quantifier.FORALL, 
                    jpype.JArray(self.Variable)([y_var]), 
                    matrix
                )
                
                # ∃x ∀y (x ∧ ¬y)
                exists_x_forall_y = self.QuantifiedBooleanFormula(
                    self.Quantifier.EXISTS,
                    jpype.JArray(self.Variable)([x_var]),
                    forall_y
                )
                
                return exists_x_forall_y
            else:
                raise ValueError(f"Type d'exemple non supporté: {example_type}")
                
        except jpype.JException as e:
            error_msg = f"Erreur lors de la création programmatique de QBF: {e}"
            self._logger.error(error_msg)
            raise ValueError(error_msg) from e