# ==============================================================================
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# The License information can be found under the "License" section of the
# README.md file.
# ==============================================================================

import copy 
import os, sys
import typing
from typing import Any, Optional, Text, Dict, List, Type
from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.training_data.message import Message

if typing.TYPE_CHECKING:
    from rasa.nlu.model import Metadata
    
root_folder = (os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 os.path.pardir)))
sys.path.append(root_folder)

from riva.nlp.nlp import get_intent_and_entities


class RivaNLPComponent(Component):
    """Riva NLP component"""

    # Which components are required by this component.
    # Listed components should appear before the component itself in the pipeline.
    @classmethod
    def required_components(cls) -> List[Type[Component]]:
        """Specify which components need to be present in the pipeline."""
        return []

    # Defines the default configuration parameters of a component
    # these values can be overwritten in the pipeline configuration
    # of the model. The component should choose sensible defaults
    # and should be able to create reasonable results with the defaults.
    defaults = {}

    # Defines what language(s) this component can handle.
    # This attribute is designed for instance method: `can_handle_language`.
    # Default value is None which means it can handle all languages.
    # This is an important feature for backwards compatibility of components.
    supported_language_list = None

    # Defines what language(s) this component can NOT handle.
    # This attribute is designed for instance method: `can_handle_language`.
    # Default value is None which means it can handle all languages.
    # This is an important feature for backwards compatibility of components.
    not_supported_language_list = None

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None) -> None:
        super().__init__(component_config)

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        """Train this component.

        This is the components chance to train itself provided
        with the training data. The component can rely on
        any context attribute to be present, that gets created
        by a call to :meth:`components.Component.pipeline_init`
        of ANY component and
        on any context attributes created by a call to
        :meth:`components.Component.train`
        of components previous to this one."""
        pass
    
    def __convert_to_rasa_intent(self, response):
        if not response["intent"]:
            print("[Riva NLU] ERROR: Intent is None in RivaNLPComponent class")
            return None
        response["intent"]['value'] = (response["intent"]['value']).replace("_yes_no","")
        response["intent"]['value'] = (response["intent"]['value']).replace("weather__temperature","weather__temprature")
        intent = {"name": response["intent"]['value'], "confidence": response["intent"]['confidence']}
        return intent
    
    def __convert_to_rasa_entities(self, response):
        """Convert model output into the Rasa NLU compatible output format."""
        for entity in response["entities"]:
            entity["extractor"] = "RivaNLPExtractor"
            if entity["entity"] == "location":
                entity2 = copy.deepcopy(entity)
                entity2["entity"] = "city"
                response["entities"].append(entity2)
        return response["entities"]

    def process(self, message: Message, **kwargs: Any) -> None:
        """Process an incoming message.

        This is the components chance to process an incoming
        message. The component can rely on
        any context attribute to be present, that gets created
        by a call to :meth:`components.Component.pipeline_init`
        of ANY component and
        on any context attributes created by a call to
        :meth:`components.Component.process`
        of components previous to this one."""
        message_dict = message.as_dict()
        if 'text' in message_dict:
            response = get_intent_and_entities(message_dict['text'])
            print("[Riva NLU] Riva Response: " + str(response))
            intent = self.__convert_to_rasa_intent(response)
            if intent:
                message.set("intent", intent, add_to_output=True)
            entities = self.__convert_to_rasa_entities(response)
            message.set("entities", entities, add_to_output=True)
        

    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        """Persist this component to disk for future loading."""
        pass

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Optional[Text] = None,
        model_metadata: Optional["Metadata"] = None,
        cached_component: Optional["Component"] = None,
        **kwargs: Any,
    ) -> "Component":
        """Load this component from file."""

        if cached_component:
            return cached_component
        else:
            return cls(meta)