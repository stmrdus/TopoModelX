"""Unit tests for SCCNN Model."""

import itertools
import random

import toponetx as tnx
import torch

from topomodelx.nn.simplicial.sccnn import SCCNN
from topomodelx.utils.sparse import from_sparse


class TestSCCNN:
    """Unit tests for the SCCNN model class."""

    def test_forward(self):
        """Test the forward method of SCCNN."""
        faces = 14
        node_creation = 17
        nodes_per_face = 3
        seed_value = 42
        random.seed(seed_value)
        torch.manual_seed(seed_value)
        # Create a random cell complex of cells with length 3
        all_combinations = list(
            itertools.combinations(
                [x for x in range(1, node_creation + 1)], nodes_per_face
            )
        )
        random.shuffle(all_combinations)
        selected_combinations = all_combinations[:faces]
        simplicial_complex = tnx.SimplicialComplex()
        for simplex in selected_combinations:
            simplicial_complex.add_simplex(simplex)
        # Some nodes might not be selected at all in the combinations above
        x_0 = torch.randn(simplicial_complex.shape[0], 2)
        x_1 = torch.randn(simplicial_complex.shape[1], 2)
        x_2 = torch.randn(faces, 2)
        in_channels_0 = x_0.shape[1]
        in_channels_1 = x_1.shape[1]
        in_channels_2 = x_2.shape[1]

        in_channels_all = (in_channels_0, in_channels_1, in_channels_2)
        incidence_1 = simplicial_complex.incidence_matrix(rank=1)
        incidence_2 = simplicial_complex.incidence_matrix(rank=2)
        laplacian_0 = simplicial_complex.hodge_laplacian_matrix(rank=0, weight=True)
        laplacian_down_1 = simplicial_complex.down_laplacian_matrix(rank=1)
        laplacian_up_1 = simplicial_complex.up_laplacian_matrix(rank=1)
        laplacian_2 = simplicial_complex.hodge_laplacian_matrix(rank=2, weight=True)

        incidence_1 = from_sparse(incidence_1)
        incidence_2 = from_sparse(incidence_2)
        laplacian_0 = from_sparse(laplacian_0)
        laplacian_down_1 = from_sparse(laplacian_down_1)
        laplacian_up_1 = from_sparse(laplacian_up_1)
        laplacian_2 = from_sparse(laplacian_2)
        conv_order = 2
        intermediate_channels_all = (16, 16, 16)
        num_layers = 2
        max_rank = 2
        model = SCCNN(
            in_channels_all=in_channels_all,
            hidden_channels_all=intermediate_channels_all,
            conv_order=conv_order,
            sc_order=max_rank,
            n_layers=num_layers,
        )
        x_all = (x_0.float(), x_1.float(), x_2.float())
        laplacian_all = (laplacian_0, laplacian_down_1, laplacian_up_1, laplacian_2)
        incidence_all = (incidence_1, incidence_2)
        with torch.no_grad():
            forward_pass = model(x_all, laplacian_all, incidence_all)
        assert torch.any(
            torch.isclose(
                forward_pass[0][0],
                torch.tensor(
                    [
                        -849.9192,
                        -1154.0405,
                        1032.2395,
                        -1020.0388,
                        -1100.6816,
                        1640.7571,
                        -2232.0454,
                        737.5161,
                        2104.5352,
                        -293.3221,
                        1316.4978,
                        3998.2910,
                        -160.5043,
                        2006.0248,
                        -876.4661,
                        -1675.6056,
                    ]
                ),
                rtol=1e-02,
            )
        )

    def test_reset_parameters(self):
        """Test the reset_parameters method of SCCNN."""
        model = SCCNN((3, 3, 3), (3, 3, 3), 2, 2, 2)
        for layer in model.children():
            if hasattr(layer, "reset_parameters"):
                layer.reset_parameters()
        for module in model.modules():
            if hasattr(module, "reset_parameters"):
                module.reset_parameters()
