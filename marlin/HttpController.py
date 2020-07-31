from flask import Flask, jsonify, make_response, request
from flask_classful import FlaskView, route
from marlin.Provider import Provider

VERSION = "0.0.1"


class HttpController(FlaskView):
    route_base = '/'
    boat = Provider().get_Boat()

    @route('/')
    def index(self):
        return make_response("OK<br>version: "+VERSION)

    @route('/state')
    def state(self):
        return jsonify(self.boat.get_state())

    @route('/start_autonomy', methods=['POST'])
    def start_autonomy(self):
        data = request.get_json()

        # TODO use json schema to validate

        if 'path' in data and self.boat.start_autonomy(data):
            return jsonify({'status': 'OK'})
        else:
            response = jsonify({'status': 'ERROR'})
            response.status_code = 503
            return response

    @route('/stop_autonomy', methods=['POST'])
    def stop_autonomy(self):
        if self.boat.stop_autonomy():
            return jsonify({'status': 'OK'})
        else:
            response = jsonify({'status': 'ERROR'})
            response.status_code = 503
            return response

    @route('/speed', methods=['POST'])
    def set_speed(self):
        data = request.get_json()
        if self.boat.set_speed(data):
            return jsonify({'status': 'OK'})
        else:
            response = jsonify({'status': 'ERROR'})
            response.status_code = 503
            return response

    @route('/pump', methods=['POST'])
    def pump(self):
        data = request.get_json()
        if self.boat.set_pump(data):
            return jsonify({'status': 'OK'})
        else:
            response = jsonify({'status': 'ERROR'})
            response.status_code = 503
            return response


if __name__ == '__main__':
    h = HttpController()
    h.start()
