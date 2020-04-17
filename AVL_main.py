from spoiler_files import Spoiler
from parapy.core import *

import kbeutils.avl as avl


class AvlAnalysis(avl.Interface):

    spoiler = Input(in_tree=True)

    @Attribute
    def configuration(self):
        return self.spoiler.avl_configuration


if __name__ == '__main__':
    from parapy.gui import display
    spoiler = Spoiler(strut_airfoil=False,
                      endplate_input=True)

    analysis = AvlAnalysis(spoiler=spoiler)
    display(analysis)
