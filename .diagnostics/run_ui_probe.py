from core.languages.basic import TwBasicInterpreter

# Create interpreter and set output callback to write directly to diagnostics log
interp = TwBasicInterpreter()

def probe_callback(text):
    with open('.diagnostics/time_warp_ui.log', 'a', encoding='utf-8') as f:
        f.write(f'callback_received: {text!r}\n')

interp.set_output_callback(probe_callback)
# Execute a few commands that produce output
interp.log_output('Hello from probe')
interp.log_output('Second line')
print('probe done')
