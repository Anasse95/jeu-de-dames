import importlib.util
import unittest
from pathlib import Path

module_path = Path(__file__).with_name('jeu_de_dameV2.py')
spec = importlib.util.spec_from_file_location('jeu_de_dameV2', module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

JeuDeDames = module.JeuDeDames
Piece = module.Piece


class TestJeuDeDames(unittest.TestCase):
    def test_un_pion_avance_vers_l_avant_sans_capture(self):
        jeu = JeuDeDames()
        jeu.plateau = [[None for _ in range(8)] for _ in range(8)]
        piece = Piece(5, 2, 'white')
        jeu.plateau[5][2] = piece

        self.assertEqual(jeu.obtenir_deplacements_valides(piece), [(4, 1), (4, 3)])
        self.assertTrue(jeu.deplacer(piece, 4, 3))
        self.assertEqual((piece.ligne, piece.col), (4, 3))

    def test_une_capture_est_obligee_quand_disponible(self):
        jeu = JeuDeDames()
        jeu.plateau = [[None for _ in range(8)] for _ in range(8)]
        piece = Piece(5, 2, 'white')
        adversaire = Piece(4, 1, 'black')
        jeu.plateau[5][2] = piece
        jeu.plateau[4][1] = adversaire

        self.assertEqual(jeu.obtenir_deplacements_valides(piece), [(3, 0)])
        self.assertFalse(jeu.deplacer(piece, 4, 3))
        self.assertTrue(jeu.deplacer(piece, 3, 0))
        self.assertIsNone(jeu.plateau[4][1])
        self.assertEqual((piece.ligne, piece.col), (3, 0))


if __name__ == '__main__':
    unittest.main()
