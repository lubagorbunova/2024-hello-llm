"""
Fine-tuning starter.
"""
# pylint: disable=too-many-locals, undefined-variable, unused-import, too-many-branches, too-many-statements
import json
from pathlib import Path

import pandas as pd

from config.constants import PROJECT_ROOT
from core_utils.llm.metrics import Metrics
from core_utils.llm.time_decorator import report_time
from lab_8_sft.main import (
    LLMPipeline,
    RawDataImporter,
    RawDataPreprocessor,
    TaskDataset,
    TaskEvaluator,
)


@report_time
def main() -> None:
    """
    Run the translation pipeline.
    """
    with open(PROJECT_ROOT / 'lab_8_sft' / 'settings.json', 'r', encoding='utf-8') as file:
        settings = json.load(file)

    importer = RawDataImporter(settings['parameters']['dataset'])
    importer.obtain()

    if isinstance(importer.raw_data, pd.DataFrame):
        preprocessor = RawDataPreprocessor(importer.raw_data)
    else:
        raise TypeError('expected pd.DataFrame')
    print(preprocessor.analyze())
    preprocessor.transform()

    dataset = TaskDataset(preprocessor.data.head(100))
    print(dataset[0])

    pipeline = LLMPipeline(settings['parameters']['model'], dataset, 120, 64, 'cpu')
    analysis = pipeline.analyze_model()
    print(analysis)
    print(pipeline.infer_sample(dataset[0]))

    predictions = pipeline.infer_dataset()

    Path(PROJECT_ROOT / 'lab_8_sft' / 'dist').mkdir(exist_ok=True)
    predictions_path = PROJECT_ROOT / 'lab_8_sft' / 'dist' / 'predictions.csv'
    predictions.to_csv(predictions_path)

    metrics_list = []
    for metric in settings['parameters']['metrics']:
        metrics_list.append(Metrics(metric))
    evaluator = TaskEvaluator(predictions_path, metrics_list)
    result = evaluator.run()
    print(result)
    assert result is not None, "Finetuning does not work correctly"


if __name__ == "__main__":
    main()
