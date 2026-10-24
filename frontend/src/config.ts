/**
 * API Configuration
 * Uses production backend URL if available, otherwise falls back to relative paths
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 
  (typeof window !== 'undefined' && window.location.hostname === 'localhost' 
    ? 'http://localhost:8000'
    : 'https://tactilecode-1.onrender.com');

export const API_ENDPOINTS = {
  UPLOAD_DIAGRAM: `${API_BASE_URL}/api/diagrams`,
  GET_SAMPLE: `${API_BASE_URL}/api/diagrams/sample/architecture`,
  GET_DIAGRAM: (id: string) => `${API_BASE_URL}/api/diagrams/${id}`,
  QUERY_NEIGHBORS: (id: string, nodeId: string) => `${API_BASE_URL}/api/diagrams/${id}/nodes/${nodeId}/neighbors`,
  QUERY_PATH: (id: string) => `${API_BASE_URL}/api/diagrams/${id}/query/path`,
  QUERY_DEPENDENTS: (id: string, nodeId: string) => `${API_BASE_URL}/api/diagrams/${id}/query/dependents`,
  QUERY_DEPENDENCIES: (id: string, nodeId: string) => `${API_BASE_URL}/api/diagrams/${id}/query/dependencies`,
  QUERY_GROUP: (id: string, groupName: string) => `${API_BASE_URL}/api/diagrams/${id}/query/group/${groupName}`,
  QUERY_GROUP_SUMMARY: (id: string, groupName: string) => `${API_BASE_URL}/api/diagrams/${id}/query/group/${groupName}/summary`,
  QUERY_ALL_GROUPS: (id: string) => `${API_BASE_URL}/api/diagrams/${id}/query/groups`,
  QUERY_REACHABLE: (id: string, nodeId: string) => `${API_BASE_URL}/api/diagrams/${id}/query/reachable/${nodeId}`,
};

export default API_ENDPOINTS;
