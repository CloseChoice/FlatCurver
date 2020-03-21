import axios from 'axios'

// eslint-disable-next-line no-unused-vars
const apiClient = axios.create({
    baseURL: 'https://immocan-backend.now.sh',
    withCredentials: false, // This is the default
    headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
    },
})

export default {}
