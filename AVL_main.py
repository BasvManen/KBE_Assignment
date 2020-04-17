from spoiler_files import Spoiler
from parapy.core import *

import kbeutils.avl as avl


class Avl_analysis(avl.Interface):

    spoiler = Input(in_tree=True)

    @Attribute
    def configuration(self):
        return self.spoiler.avl_configuration

    case_settings = Input()

    @Part
    def cases(self):
        return avl.Case(name=self.case_settings[child.index][0],
                        settings=self.case_settings[child.index][1])


if __name__ == '__main__':
    from parapy.gui import display
    spoiler = Spoiler(strut_airfoil=False,
                      endplate_input=True)

    cases = [('fixed aoa', {'alpha': 3})]

    analysis = Avl_analysis(spoiler=spoiler,
                            case_settings=cases)
    display(analysis)
