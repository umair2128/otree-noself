from os import environ

SESSION_CONFIGS = [
    dict(
        name='double_auction',
        display_name="Double Auction",
        app_sequence=['double_auction'],
        num_units=3,
        num_rounds=3,
        num_demo_participants=4,
        timeout_seconds=7200,
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
