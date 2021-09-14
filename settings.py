from os import environ

SESSION_CONFIGS = [
    dict(
        name='double_auction',
        display_name="Double Auction",
        app_sequence=['double_auction'],
        num_rounds=15,
        num_demo_participants=4,
        timeout_seconds=600,
        wait_timeout_seconds=5,
        multiple_unit_trading=True,
        relative_price_imp="self",
        num_types=1,
        num_induc_val_steps=5,
        quant_at_indc_val=0,
        eq_indc_val_step=4,
        step_diff_per_type=5,
        min_induc_val=20,
        step_up_aft_ev_round=3,
        step_up_by=5,
        doc="""
        This is the commodity double auction application. The following passage discusses the configurable parameters for
        this app. 
        """
        """num_rounds: The number of periods for which the subjects will participate in the commodity double auction. 
        Please enter an integer value of 1 or more. 
        """
        """timeout_seconds: The amount of time (in seconds) each subject will have in every period for carrying out trades.
        """
        """wait_timeout_seconds: The amount of time (in seconds) for which the subjects would have to wait at the end of 
        each trading period before the next period begins.
        """
        """multiple_unit_trading: Set to 'True' (without quotes) if subjects are allowed to bid/ask or buy/sell multiple
        units in each offer they make, otherwise set to 'False' (without quotes).
        """
        """relative_price_imp: Set to "all" (WITH quotes) to enforce price improvement relative to the current best offer, 
        otherwise set to "self" (WITH quotes) to enforce price improvement relative to own best offer.
        """
        """num_types: If all buyers are to have the same set of induced values (and similar logic applies to the sellers), 
        then set to '1' (without quotes), otherwise set to '2' (without quotes) for two groups of buyers/sellers each with
        different sets of induced values.
        """
        """num_induc_val_steps: The number of steps of induced values for each type of buyers/sellers.
        """
        """quant_at_indc_val: Enter the fixed number units endowed at each step of induced values. The default value at '0'
        (without quotes) implies a declining endowment from one step of induced values to the next for buyers/sellers.
        """
        """eq_indc_val_step: The number of steps of induced values for each type of buyers/sellers for which it is, in 
        theory, optimal for them to carry out trade. This number must be less than or equal to the number you entered for
        'num_induc_val_steps'.
        """
        """step_diff_per_type: The amount of difference between two consecutive steps of induced values for each type 
        of buyers/sellers. 
        """
        """min_induc_val: The lower threshold for induced values. Subjects' induced values will not be lower than this amount. 
        """
        """step_up_aft_ev_round: After every 'x' number of rounds, subjects' induced values at each step will be shifted upwards
        by a given amount. Here you are required to enter the number 'x'. This number must be less than or equal to
        the number you entered for 'num_rounds'.
        """
        """step_up_by: The amount by which, after every 'x' number of rounds, subjects' induced values at each step will 
        be shifted upward.
        """
    ),
    dict(
        name='dollar_auction',
        display_name="Dollar Auction",
        app_sequence=['dollar_auction'],
        num_demo_participants=3,
    ),
    dict(
        name='guess_two_thirds',
        display_name="Guess 2/3 of the average",
        app_sequence=['guess_two_thirds'],
        num_demo_participants=3,
    ),
    dict(
        name='prisoner',
        display_name="Prisoner's Dilemma",
        app_sequence=['prisoner'],
        num_demo_participants=2,
    ),
    dict(
        name='stroop',
        app_sequence=['stroop'],
        num_demo_participants=1
    ),
    dict(
        name='go_no_go',
        display_name='Go/No-Go task',
        app_sequence=['go_no_go'],
        num_demo_participants=1,
    ),
    dict(
        name='randomize_stimuli',
        display_name='Demo of different stimulus randomizations',
        app_sequence=['randomize_stimuli'],
        num_demo_participants=5,
    ),
    dict(
        name='quiz',
        app_sequence=['quiz'],
        num_demo_participants=1
    ),
    dict(
        name='bigfive',
        display_name='Big 5 personality test',
        app_sequence=['bigfive'],
        num_demo_participants=1,
    ),
    dict(
        name='nim',
        display_name="Race game / Nim (take turns adding numbers to reach a target)",
        app_sequence=['nim'],
        num_demo_participants=2,
    ),
    dict(
        name='rockpaperscissors',
        app_sequence=['rockpaperscissors'],
        num_demo_participants=2),
    dict(
        name='tictactoe',
        app_sequence=['tictactoe'],
        num_demo_participants=2),
    dict(
        name='monty_hall',
        display_name="Monty Hall (3-door problem from 'The Price is Right')",
        app_sequence=['monty_hall'],
        num_demo_participants=1,
    ),
    dict(
        name='DA',
        display_name="My DA",
        num_demo_participants=4,
        num_rounds=2,
        buyer_=[0.3, 0.75, 0.3],
        app_sequence=['DA'],
        doc="",
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(real_world_currency_per_point=1.00, participation_fee=0.00, doc="")

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '4387860144726'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']

PARTICIPANT_FIELDS = ['stimuli', 'responses', 'reaction_times', 'order']
SESSION_FIELDS = ['num_induc_val_steps', 'quant_at_indc_val', 'min_induc_val', 'num_types', 'eq_indc_val_step', 'step_diff_per_type', 'step_up_aft_ev_round', 'step_up_by', 'starting_price','ending_price','total_rounds','timeout_seconds','presets_template', 'seller_presets', 'seller_type1_presets', 'seller_type2_presets','buyer_presets', 'buyer_type1_presets','buyer_type2_presets']