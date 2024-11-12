import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  final String baseUrl = 'http://192.168.1.140:3000';
  
  Future<Map<String, dynamic>> triggerSearch() async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/trigger-search'),
        headers: {
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final result = json.decode(response.body);
        if (result['success']) {
          // Just return the result, don't send email
          return result;
        } else {
          throw Exception(result['error'] ?? 'Unknown error');
        }
      } else {
        throw Exception('Server error: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }
}