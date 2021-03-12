import firebase from 'firebase/app'
import 'firebase/firestore'

const firebaseConfig = {
  apiKey: "AIzaSyC9yvIbWYwznB5KEweOdpOPBRNvPRh8IaM",
  authDomain: "crud-80669.firebaseapp.com",
  projectId: "crud-80669",
  storageBucket: "crud-80669.appspot.com",
  messagingSenderId: "840972488143",
  appId: "1:840972488143:web:d48196527afde6a22e16ba"
}

export const firebaseApp = firebase.initializeApp(firebaseConfig)