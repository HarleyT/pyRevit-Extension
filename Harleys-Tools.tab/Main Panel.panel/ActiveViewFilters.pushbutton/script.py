# -*- coding: utf-8 -*-
__title__ = "Active View Filters"                           # Name of the button displayed in Revit UI
__doc__ = """Version = 1.0
Date    = 08.06.2022
_____________________________________________________________________
Description:
Dockable Panel showing all filters for the Active View.
_____________________________________________________________________
Last update:
- [08.06.2022] - 1.0 RELEASE
_____________________________________________________________________
To-Do:
- Show all filters in active view
- make it a dockable panel
- add functionality of original filters (visibility on/off, projection/cut overrides etc.)
_____________________________________________________________________
Author: Harley Trappitt"""                          # Button Description shown in Revit UI


#   You need to use 'os' package to get all files in the given folder with 'os.listdir'.
#   Then you can filter family files and iterate through them to open each and make a change.
#ModelPath = ModelPathUtils.ConvertUserVisiblePathToModelPath(path_to_rfa)
#options = OpenOptions()
#rvt_doc = app.OpenDocumentFile(ModelPath, options)
#   Then make your changes to rvt_doc and close it.

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ==================================================
# Regular + Autodesk
import os, sys, math, datetime, time                                    # Regular Imports
from Autodesk.Revit.DB import *                                         # Import everything from DB (Very good for beginners)
from Autodesk.Revit.DB import Transaction, FilteredElementCollector     # or Import only classes that are used.

# pyRevit
from pyrevit import revit, forms                                        # import pyRevit modules. (Lots of useful features)
from pyrevit import DB, UI
from pyrevit.framework import Input
from pyrevit import script
from pyrevit import HOST_APP, framework, coreutils, PyRevitException
from pyrevit import revit, DB, UI
from pyrevit import forms, script
from pyrevit.framework import wpf, ObservableCollection

# Custom Imports
# from Snippets._selection import get_selected_elements                   # lib import
# from Snippets._convert import convert_internal_to_m                     # lib import

# .NET Imports
import clr                                  # Common Language Runtime. Makes .NET libraries accessinble
clr.AddReference("System")                  # Refference System.dll for import.
from System.Collections.Generic import List # List<ElementType>() <- it's special type of list from .NET framework that RevitAPI requires
# List_example = List[ElementId]()          # use .Add() instead of append or put python list of ElementIds in parentesis.

clr.AddReference("RevitServices")
import RevitServices
#from RevitServices.Persistence import DocumentManager
#doc = DocumentManager.Instance.CurrentDBDocument
clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)

# WPF Dependencies
clr.AddReference('System.Windows.Forms')
clr.AddReference('IronPython.Wpf')

# find the path of ui.xaml
from pyrevit import UI
from pyrevit import script
xamlfile = script.get_bundle_file('ui.xaml')

# import WPF creator and base Window
import wpf
from System import Windows

from System.Collections.ObjectModel import ObservableCollection
from System.ComponentModel import INotifyPropertyChanged, PropertyChangedEventArgs
from System.Windows.Input import ICommand
from System.Windows import Controls
from System import ComponentModel
import pyevent


# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
doc = __revit__.ActiveUIDocument.Document   # Document   class from RevitAPI that represents project. Used to Create, Delete, Modify and Query elements from the project.
uidoc = __revit__.ActiveUIDocument          # UIDocument class from RevitAPI that represents Revit project opened in the Revit UI.
app = __revit__.Application                 # Represents the Autodesk Revit Application, providing access to documents, options and other application wide data and settings.
PATH_SCRIPT = os.path.dirname(__file__)     # Absolute path to the folder where script is placed.
#uidoc = HOST_APP.uidoc

current_view = doc.ActiveView

# GLOBAL VARIABLES

# - Place global variables here.

# ╔═╗╦ ╦╔╗╔╔═╗╔╦╗╦╔═╗╔╗╔╔═╗
# ╠╣ ║ ║║║║║   ║ ║║ ║║║║╚═╗
# ╚  ╚═╝╝╚╝╚═╝ ╩ ╩╚═╝╝╚╝╚═╝ FUNCTIONS
# ==================================================

# - Place local functions here. If you might use any functions in other scripts, consider placing it in the lib folder.

def refresh_active_view():
    uidoc.RequestViewChange(current_view)
    uidoc.RefreshActiveView()
    doc.Regenerate()

# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝ CLASSES
# ==================================================

# - Place local classes here. If you might use any classes in other scripts, consider placing it in the lib folder.

class _WPFPanelProvider(UI.IDockablePaneProvider):
    def __init__(self, panel_type, default_visible=True):
        self._panel_type = panel_type
        self._default_visible = default_visible
        self.panel = self._panel_type()

    def update_list(self):
        try:
            template_list = [forms.TemplateListItem(s.IntegerValue) for s in selected]
            self.selected_lb.ItemsSource = ObservableCollection[forms.TemplateListItem](template_list)
        except Exception as e:
            print e.message

    def refresh_active_view(current_view):
        uidoc.RequestViewChange(current_view)
        uidoc.RefreshActiveView()
        doc.Regenerate()

    def active_filters(self):
        pass

class Reactive(ComponentModel.INotifyPropertyChanged):
    """WPF property updator base mixin"""
    PropertyChanged, _propertyChangedCaller = pyevent.make_event()

    def add_PropertyChanged(self, value):
        self.PropertyChanged += value

    def remove_PropertyChanged(self, value):
        self.PropertyChanged -= value

    def OnPropertyChanged(self, prop_name):
        if self._propertyChangedCaller:
            args = ComponentModel.PropertyChangedEventArgs(prop_name)
            self._propertyChangedCaller(self, args)

class Command(ICommand):
    def __init__(self, execute):
        self.execute = execute

    def Execute(self, parameter):
        self.execute()

    def add_CanExecuteChanged(self, handler):
        pass

    def remove_CanExecuteChanged(self, handler):
        pass

    def CanExecute(self, parameter):
        return True

class MyWindow(Windows.Window):
    def __init__(self):
        wpf.LoadComponent(self, xamlfile)

    def active_filters(self, sender, args):
        pass

    def add_filters():
        pass

    def remove_filters():
        pass

    def edit_filters():
        pass


# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ==================================================
#if __name__ == '__main__':
    # START CODE HERE




projRGBList, cutRGBList, surForPatList, surBacPatList, cutForPatList, cutBacPatList, transList, halfList, prweList = [],[],[],[],[],[],[],[],[]
prPatList, cutweList, cutPatList, surForList, surBacList, cutForList, cutBacList, elementList, nameList = [],[],[],[],[],[],[],[],[]
visibilitiesList, categories = [],[]

current_view = doc.ActiveView
view_filters = {}

filters = current_view.GetFilters()

elements, elementName, visibilities, listtrans, listhalf = [],[],[],[],[]

for f in filters:
    #if element:
    #    view_filters[
    #        "%s: %s" % (element.Name, visibilities)
    #    ] = elements

    visibilities.append(current_view.GetFilterVisibility(f))
    element=doc.GetElement(f)
    elements.append(element)
    elementName.append(element.Name)
    filterObject = current_view.GetFilterOverrides(f)
    listtrans.append(filterObject.Transparency)
    listhalf.append(filterObject.Halftone)

		
transList.Add(listtrans)
halfList.Add(listhalf)
visibilitiesList.append(visibilities)
elementList.append(elements)
nameList.append(elementName)


# Let's show the window (modal)
MyWindow().ShowDialog()


################################################################################################
#family_dict = {}
#for e in revit.query.get_all_elements_in_view(active_view):
#    try:
#        e_type = revit.query.get_type(e)
#        family = e_type.Family
#        if family.FamilyCategory:
#            family_dict[
#                "%s: %s" % (family.FamilyCategory.Name, family.Name)
#            ] = family
#    except:
#        pass
#if family_dict:
#    selected_families = forms.SelectFromList.show(
#        sorted(family_dict.keys()),
#        title="Select Families",
#        multiselect=True,
#    )
################################################################################################


# AVOID  placing Transaction inside of your loops! It will drastically reduce perfomance of your script.
t = Transaction(doc,__title__)  # Transactions are context-like objects that guard any changes made to a Revit model.

# You need to use t.Start() and t.Commit() to make changes to a Project.
t.Start()  # <- Transaction Start

#- CHANGES TO REVIT PROJECT HERE

t.Commit()  # <- Transaction End

# Notify user that script is complete.
print('Script is finished.')