"""
Copyright 2021 AI Singapore

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from pathlib import Path
from unittest import TestCase, mock

import cv2
import numpy as np
import numpy.testing as npt
import pytest
import yaml

from peekingduck.pipeline.nodes.model.mtcnn import Node
from peekingduck.pipeline.nodes.model.mtcnnv1.mtcnn_files.detector import Detector


@pytest.fixture
def mtcnn_config():
    filepath = (
        Path.cwd()
        / "tests"
        / "pipeline"
        / "nodes"
        / "model"
        / "mtcnnv1"
        / "test_mtcnn.yml"
    )
    with open(filepath) as file:
        node_config = yaml.safe_load(file)
    node_config["root"] = Path.cwd()

    return node_config


@pytest.fixture()
def mtcnn(mtcnn_config):
    node = Node(mtcnn_config)

    return node


@pytest.fixture()
def mtcnn_detector(mtcnn_config):
    detector = Detector(mtcnn_config)

    return detector


def replace_download_weights(root, blob_file):
    return False


@pytest.mark.mlmodel
class TestMtcnn:
    def test_no_human_face_image(self, test_no_human_images, mtcnn):
        blank_image = cv2.imread(test_no_human_images)
        output = mtcnn.run({"img": blank_image})
        expected_output = {
            "bboxes": np.empty((0, 4), dtype=np.float32),
            "bbox_scores": np.empty((0), dtype=np.float32),
            "bbox_labels": np.empty((0)),
        }
        assert output.keys() == expected_output.keys()
        npt.assert_equal(output["bboxes"], expected_output["bboxes"])
        npt.assert_equal(output["bbox_scores"], expected_output["bbox_scores"])
        npt.assert_equal(output["bbox_labels"], expected_output["bbox_labels"])

    def test_return_at_least_one_face_and_one_bbox(self, test_human_images, mtcnn):
        test_img = cv2.imread(test_human_images)
        output = mtcnn.run({"img": test_img})
        assert "bboxes" in output
        assert output["bboxes"].size != 0

    def test_no_weights(self, mtcnn_config):
        with mock.patch(
            "peekingduck.weights_utils.checker.has_weights", return_value=False
        ), mock.patch(
            "peekingduck.weights_utils.downloader.download_weights",
            wraps=replace_download_weights,
        ), TestCase.assertLogs(
            "peekingduck.pipeline.nodes.model.mtcnnv1.mtcnn_model.logger"
        ) as captured:
            mtcnn = Node(config=mtcnn_config)
            # records 0 - 20 records are updates to configs
            assert (
                captured.records[0].getMessage()
                == "---no mtcnn weights detected. proceeding to download...---"
            )
            assert (
                captured.records[1].getMessage()
                == "---mtcnn weights download complete.---"
            )
            assert mtcnn is not None

    def test_model_initialization(self, mtcnn_config):
        detector = Detector(config=mtcnn_config)
        model = detector.mtcnn
        assert model is not None
