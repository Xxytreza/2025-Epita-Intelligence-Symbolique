from typing import List
# argumentation_analysis/agents/core/logic/logic_factory.py
"""
Factory pour créer les agents logiques appropriés.
"""

import logging
from typing import Dict, Optional, Any, Type

from semantic_kernel import Kernel

from .abstract_logic_agent import AbstractLogicAgent
from .propositional_logic_agent import PropositionalLogicAgent
from .first_order_logic_agent import FirstOrderLogicAgent
from .modal_logic_agent import ModalLogicAgent
from .qbf_logic_agent import QBFLogicAgent

# Configuration du logger
logger = logging.getLogger("Orchestration.LogicAgentFactory")

class LogicAgentFactory:
    """
    Factory pour créer les agents logiques appropriés.
    
    Cette classe permet de créer des instances d'agents logiques
    en fonction du type de logique spécifié.
    """
    
    # Mapping des types de logique vers les classes d'agents
    _agent_classes: Dict[str, Type[AbstractLogicAgent]] = {
        "propositional": PropositionalLogicAgent,
        "first_order": FirstOrderLogicAgent,
        "modal": ModalLogicAgent,
        "quantified_boolean": QBFLogicAgent
    }
    
    @classmethod
    def create_agent(cls, logic_type: str, kernel: Kernel, llm_service: Optional[Any] = None) -> Optional[AbstractLogicAgent]:
        """
        Crée une instance d'un agent logique basé sur le type de logique spécifié.

        Recherche la classe d'agent correspondante dans `_agent_classes`, l'instancie
        avec le `kernel` fourni, et configure ses composants avec `llm_service` si présent.

        :param logic_type: Le type de logique pour lequel créer l'agent
                           (par exemple, "propositional", "first_order", "modal", "qbf").
                           La casse est ignorée et les espaces sont supprimés.
        :type logic_type: str
        :param kernel: L'instance du `semantic_kernel.Kernel` à passer à l'agent.
        :type kernel: Kernel
        :param llm_service: Le service LLM optionnel à utiliser pour configurer
                            les composants de l'agent.
        :type llm_service: Optional[Any]
        :return: Une instance de la sous-classe `AbstractLogicAgent` correspondante,
                 ou None si le `logic_type` n'est pas supporté ou si une erreur survient.
        :rtype: Optional[AbstractLogicAgent]
        """
        logger.info(f"Création d'un agent logique de type '{logic_type}'")
        
        # Normaliser le type de logique
        normalized_logic_type = logic_type.lower().strip()
        
        # Support des aliases pour une meilleure ergonomie
        type_aliases = {
            "pl": "propositional",
            "fol": "first_order",
            "ml": "modal",
            "qbf": "quantified_boolean"
        }
        
        # Résoudre les aliases
        if normalized_logic_type in type_aliases:
            normalized_logic_type = type_aliases[normalized_logic_type]
        
        # Vérifier si le type de logique est supporté
        if normalized_logic_type not in cls._agent_classes:
            logger.error(f"Type de logique non supporté: {logic_type}")
            logger.info(f"Types supportés: {', '.join(cls._agent_classes.keys())}")
            logger.info(f"Aliases supportés: {', '.join(type_aliases.keys())}")
            return None
        
        try:
            # Créer l'instance de l'agent
            agent_class = cls._agent_classes[normalized_logic_type]
            agent = agent_class(kernel)
            
            # Configurer le kernel de l'agent si un service LLM est fourni
            if llm_service:
                agent.setup_agent_components(llm_service)
            
            logger.info(f"Agent logique de type '{logic_type}' créé avec succès")
            return agent
        
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'agent logique de type '{logic_type}': {str(e)}", exc_info=True)
            return None
    
    @classmethod
    def register_agent_class(cls, logic_type: str, agent_class: Type[AbstractLogicAgent]) -> None:
        """
        Enregistre une nouvelle classe d'agent pour un type de logique spécifique.

        Permet d'étendre dynamiquement les types d'agents logiques que la factory peut créer.

        :param logic_type: Le nom du type de logique (sera normalisé en minuscules et sans espaces).
        :type logic_type: str
        :param agent_class: La classe de l'agent (doit hériter de `AbstractLogicAgent`).
        :type agent_class: Type[AbstractLogicAgent]
        :return: None
        :rtype: None
        """
        logger.info(f"Enregistrement de la classe d'agent '{agent_class.__name__}' pour le type de logique '{logic_type}'")
        cls._agent_classes[logic_type.lower().strip()] = agent_class
    
    @classmethod
    def get_supported_logic_types(cls) -> List[str]:
        """
        Retourne la liste des types de logique actuellement supportés par la factory.

        :return: Une liste des noms des types de logique enregistrés.
        :rtype: List[str]
        """
        return list(cls._agent_classes.keys())
    
    @classmethod
    def get_supported_logic_types_with_aliases(cls) -> Dict[str, str]:
        """
        Retourne un dictionnaire des types de logique supportés avec leurs aliases.

        :return: Un dictionnaire mapping alias -> type de logique réel.
        :rtype: Dict[str, str]
        """
        base_types = list(cls._agent_classes.keys())
        aliases = {
            "pl": "propositional",
            "fol": "first_order", 
            "ml": "modal",
            "qbf": "quantified_boolean"
        }
        
        # Créer le mapping complet
        all_types = {}
        
        # Ajouter les types de base
        for base_type in base_types:
            all_types[base_type] = base_type
            
        # Ajouter les aliases
        for alias, base_type in aliases.items():
            if base_type in base_types:
                all_types[alias] = base_type
                
        return all_types
    
    @classmethod
    def is_logic_type_supported(cls, logic_type: str) -> bool:
        """
        Vérifie si un type de logique (ou son alias) est supporté.

        :param logic_type: Le type de logique à vérifier.
        :type logic_type: str
        :return: True si le type est supporté, False sinon.
        :rtype: bool
        """
        normalized_logic_type = logic_type.lower().strip()
        
        # Vérifier les types directs
        if normalized_logic_type in cls._agent_classes:
            return True
            
        # Vérifier les aliases
        type_aliases = {
            "pl": "propositional",
            "fol": "first_order",
            "ml": "modal", 
            "qbf": "quantified_boolean"
        }
        
        if normalized_logic_type in type_aliases:
            return type_aliases[normalized_logic_type] in cls._agent_classes
            
        return False
    
    @classmethod
    def get_agent_capabilities_summary(cls) -> Dict[str, Dict[str, str]]:
        """
        Retourne un résumé des capacités de chaque type d'agent supporté.

        :return: Dictionnaire avec les informations sur chaque type d'agent.
        :rtype: Dict[str, Dict[str, str]]
        """
        capabilities = {
            "propositional": {
                "name": "PropositionalLogicAgent",
                "description": "Agent pour la logique propositionnelle avec connecteurs logiques",
                "syntax": "Propositions atomiques, connecteurs: !, ||, &&, =>, <=>"
            },
            "first_order": {
                "name": "FirstOrderLogicAgent", 
                "description": "Agent pour la logique du premier ordre avec quantificateurs et prédicats",
                "syntax": "Prédicats, variables, constantes, quantificateurs: forall, exists"
            },
            "modal": {
                "name": "ModalLogicAgent",
                "description": "Agent pour la logique modale avec opérateurs de nécessité et possibilité",
                "syntax": "Opérateurs modaux: []p (nécessité), <>p (possibilité)"
            },
            "quantified_boolean": {
                "name": "QBFLogicAgent",
                "description": "Agent pour la logique des formules booléennes quantifiées",
                "syntax": "Variables booléennes, quantificateurs: exists, forall sur variables booléennes"
            }
        }
        
        # Retourner seulement les capacités des agents actuellement enregistrés
        return {logic_type: capabilities[logic_type] 
                for logic_type in cls._agent_classes.keys() 
                if logic_type in capabilities}