"""
This script is to be run on Tropo
"""

def wait_for_signal():
    while True:
        event = say("http://www.phono.com/audio/holdmusic.mp3 http://www.phono.com/audio/holdmusic.mp3") #, {onSignal: make_call_handler})
        if event.name == 'signal':
            yield event.value
        else:
            break
        
def make_call(number):
    log('***************************************')
    log('making call to:')
    log(number)
    say('Connecting. At the end of the call, press star and stay on the line, so we can automatically connect to the next person on your list')
    log('***************************************')
    log('dialing')
    transfer_params = {
            'allowSignals': '',
            'answerOnMedia': True,
            'callerID': '+1 603-413-2927',
            'terminator': '*',
        }
    transfer_event = transfer(number, transfer_params)
    log('********************************')
    log('transfer event')
    log(transfer_event)
    log('transfer event.__dict__')
    log(transfer_event.__dict__)
    log(transfer_event.connectedDuration)
    log("transfer_event.value")
    val = getattr(transfer_event, 'value', None)
    log(val)
    log("transfer_event.value.__dict__")
    log(val.__dict__)
    call = getattr(transfer_event, 'value', None)
    if not getattr(call, 'answeredTime'):
        return say('We seem to be having trouble connecting to that number. Please press wrong info, then connect to the next voter')
    else:
        return say('Great. Submit your responses for this call, then press the "place call" button to dial the next person on your list')

log('***************************************')
log('starting call')
call('+1' + number, {'callerID': '+1 603-413-2927'})
event = say('Welcome to the MayDay call tool! Press the "start calling" button to begin dialing')
if event.name == 'signal':
    # signal sent before wait began
    make_call(event.value)

for number in wait_for_signal():
    log('passing off to make_call()')
    event = make_call(number)
    while event.name == 'signal':
        # signal sent before wait began
        event = make_call(event.value)

log('exiting')
# name == 'choice'; value == None
log('***************************************')
log('not calling')
say("Sorry you're having trouble. Please press the call me again button when you're ready to start")
