
from typing import Union, List, Dict
from pymodaq.control_modules.move_utility_classes import (DAQ_Move_base, comon_parameters_fun,
                                                          main, DataActuatorType, DataActuator)

from pymodaq_utils.utils import ThreadCommand  # object used to send info back to the main thread
from pymodaq_gui.parameter import Parameter

from lakeshore import Model335


class DAQ_Move_335Heater(DAQ_Move_base):
    """ Instrument plugin class for an actuator.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Move module through inheritance via
    DAQ_Move_base. It makes a bridge between the DAQ_Move module and the Python wrapper of a particular instrument.

    TODO Complete the docstring of your plugin with:
        * The set of controllers and actuators that should be compatible with this instrument plugin.
        * With which instrument and controller it has been tested.
        * The version of PyMoDAQ during the test.
        * The version of the operating system.
        * Installation instructions: what manufacturer’s drivers should be installed to make it run?

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.
         
    # TODO add your particular attributes here if any

    """
    is_multiaxes = False  # TODO for your plugin set to True if this plugin is controlled for a multiaxis controller
    #_axis_names: Union[List[str], Dict[str, int]] = ['Axis1', 'Axis2']  # TODO for your plugin: complete the list
    #_controller_units: Union[str, List[str]] = 'K'  # TODO for your plugin: put the correct unit here, it could be
    # TODO  a single str (the same one is applied to all axes) or a list of str (as much as the number of axes)
    #_epsilon: Union[float, List[float]] = 0.1  # TODO replace this by a value that is correct depending on your controller
    # TODO it could be a single float of a list of float (as much as the number of axes)
    #data_actuator_type = DataActuatorType.DataActuator  # wether you use the new data style for actuator otherwise set this
    # as  DataActuatorType.float  (or entirely remove the line)
    params = comon_parameters+[
        {'title': 'Address:', 'name': 'address', 'type': 'str',
                 'value': 'COM6', 'readonly': False},
        {'title': 'Input:', 'name': 'input', 'type': 'str',
                'value': 'TWO_INPUT_A', 'readonly': False}, #could be INPUT_A, TWO_INPUT_A, INPUT_B, TWO_INPUT_B
        {'title': 'Heater Resistance [Ohm]:', 'name': 'resistance', 'type': 'float',
                'value': 'HEATER_50_OHM', 'readonly': False}, #could be HEATER_50_OHM, ...
        {'title': 'Max Current [A]:', 'name': 'max_current', 'type': 'float',
                'value': '1', 'readonly': False},
        {'title': 'Ramp Rate [K/min]:', 'name': 'ramp_rate', 'type': 'float', #
                'value': '1', 'readonly': False},
        {'title': 'P:', 'name': 'p', 'type': 'float',  #
                'value': '50', 'readonly': False},
        {'title': 'I:', 'name': 'i', 'type': 'float',  #
                'value': '20', 'readonly': False},
        {'title': 'D:', 'name': 'd', 'type': 'float',  #
                'value': '0', 'readonly': False},
        {'title': 'Setpoint  [K]:', 'name': 'setpoint', 'type': 'float',  #
                'value': '77', 'readonly': False},
        {'title': 'Heater Status:', 'name': 'heater_status', 'type': 'float',  #
                'value': 'LOW', 'readonly': False}, #could be OFF, HIGH, LOW, ...
    #     ]
    # TODO some of these params should be displayed as list of options ?
    # params = [  {'title': 'Address:', 'name': 'address', 'type': 'str',
    #              'value': 'COM6', 'readonly': False},
    #             {'title': 'Setpoint  [K]:', 'name': 'setpoint', 'type': 'float',  #
    #             'value': '310', 'readonly': False} # TODO for your custom plugin: elements to be added here as dicts in order to control your custom stage
    #             ] + comon_parameters_fun(is_multiaxes, axis_names=_axis_names, epsilon=_epsilon)
    # # _epsilon is the initial default value for the epsilon parameter allowing pymodaq to know if the controller reached
    # # the target value. It is the developer responsibility to put here a meaningful value

    def ini_attributes(self):
        #  TODO declare the type of the wrapper (and assign it to self.controller) you're going to use for easy
        #  autocompletion
        self.controller: Model335 = None

        #TODO declare here attributes you want/need to init with a default value
        pass

    def get_actuator_value(self):
        """Get the current value from the hardware with scaling conversion.

        Returns
        -------
        float: The position obtained after scaling conversion.
        """
        pos = self.controller.get_control_setpoint(1) #get current setpoint for output 1
        pos = self.get_position_with_scaling(pos)
        return pos

    def user_condition_to_reach_target(self) -> bool:
        """ Implement a condition for exiting the polling mechanism and specifying that the
        target value has been reached

       Returns
        -------
        bool: if True, PyMoDAQ considers the target value has been reached
        """
        #todo RAMP RATE
        # TODO either delete this method if the usual polling is fine with you, but if need you can
        #  add here some other condition to be fullfilled either a completely new one or
        #  using or/and operations between the epsilon_bool and some other custom booleans
        #  for a usage example see DAQ_Move_brushlessMotor from the Thorlabs plugin
        return True

    def close(self):
        """Terminate the communication protocol"""
        ## TODO for your custom plugin
        # raise NotImplementedError  # when writing your own plugin remove this line
        if self.is_master:
            self.controller.disconnect_usb()  # when writing your own plugin replace this line

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        ## TODO for your custom plugin
        ## TODO pid,
        if param.name() == "address":
            self.controller = Model335(baud_rate = 57600, com_port = self.settings.child("address").value())  #instantiate you driver with whatever arguments are needed
        elif param.name() == "input":
            display_ = self.params('Input')
            self.controller.set_display_setup(self.controller.DisplaySetup.display_)
        elif param.name() == "resistance":
            heater_resistance = self.params('resistance')
            self.controller.set_heater_setup_one(self.controller.HeaterResistance.heater_resistance, 1.0,
                                                 self.controller.HeaterOutputDisplay.POWER)  # TODO : make the heater display a variable
        elif param.name() == "setpoint":
            set_point = self.params('setpoint')
            self.controller.set_control_setpoint(1, set_point)
        elif param.name() == "heater_status":
            heater_range = self.params('heater_status')
            self.controller.set_heater_range(1, self.controller.HeaterRange.heater_range)


        else:
            pass

    def ini_stage(self, controller=None):
        """Actuator communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator by controller (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """

        if self.is_master:
            self.controller = Model335(baud_rate = 57600, com_port = self.settings.child("address").value())  #instantiate you driver with whatever arguments are needed

            # Configure the display mode
            display_ = self.params('Input')
            print(display)
            self.controller.set_display_setup(self.controller.DisplaySetup.display_)

            # Configure heater output 1 using the HeaterSetup class and set_heater_setup method
            heater_resistance = self.params('resistance')
            self.controller.set_heater_setup_one(self.controller.HeaterResistance.heater_resistance, 1.0,
                                              self.controller.HeaterOutputDisplay.POWER) #TODO : make the heater display a variable

            # Configure heater output 1 to the setpoint
            set_point = self.params('setpoint')
            self.controller.set_control_setpoint(1, set_point)

            # Turn on the heater by setting the range
            heater_range = self.params('heater_status')
            self.controller.set_heater_range(1, self.controller.HeaterRange.heater_range)

            initialized = True

        else:
            self.controller = controller
            initialized = True

        info = "Initialized connection."
        return info, initialized

    def move_abs(self, value: DataActuator):
        """ Move the actuator to the absolute target defined by value

        Parameters
        ----------
        value: (float) value of the absolute target positioning
        """

        value = self.check_bound(value)  #if user checked bounds, the defined bounds are applied here
        self.target_value = value
        value = self.set_position_with_scaling(value)  # apply scaling if the user specified one
        self.controller.set_control_setpoint(1, value)
        self.emit_status(ThreadCommand('Update_Status', ['Changed setpoint to {}K'.format(value)]))

    def move_rel(self, value: DataActuator):
        """ Move the actuator to the relative target actuator value defined by value

        Parameters
        ----------
        value: (float) value of the relative target positioning
        """
        value = self.check_bound(self.current_position + value) - self.current_position
        self.target_value = value + self.current_position
        value = self.set_position_relative_with_scaling(value)
        self.controller.set_control_setpoint(1, value)
        self.emit_status(ThreadCommand('Update_Status', ['Changed setpoint to {}K'.format(value)]))

    def move_home(self):
        """Call the reference method of the controller"""

        # Configure heater output 1 to a home setpoint
        home_setpoint = 77 #TODO make this a variable
        self.controller.set_control_setpoint(1, home_setpoint)
        self.emit_status(ThreadCommand('Update_Status', ['Changed setpoint to {}K'.format(home_setpoint)]))

    def stop_motion(self):
        """Stop the actuator and emits move_done signal"""

        ## TODO for your custom plugin
        raise NotImplementedError  # when writing your own plugin remove this line
        kelvin_reading = self.controller.get_kelvin_reading(1)
        self.controller.set_control_setpoint(1, kelvin_reading)
        self.emit_status(ThreadCommand('Update_Status', ['Changed setpoint to current value {}K'.format(kelvin_reading)]))


if __name__ == '__main__':
    main(__file__)
