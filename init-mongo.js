//fichier init-mongo.js de configuration des rôles utilisate.urs

db = db.getSiblingDB('admin');

// Création de l'utilisateur root (admin)
//db.createUser({
//  user: "admin",
//  pwd: "admin",
//  roles: [ { role: "root", db: "admin" } ]
//});

// Création de l'utilisateur data_migrator avec accès en lecture/écriture
// La création de data_migrator se fait bien dans le contexte de la DB admin
db.createUser({
  user: "data_migrator",
  pwd: "data_migrator",
  roles: [
    //{ role: "readWrite", db: "test2" },
    { role: "dbOwner", db: "test2" } // <-- AJOUTER dbOwner pour un contrôle total de la BD
  ]
});

db = db.getSiblingDB('test2');

//Création de l'utilisateur analyst avec accès en lecture seule
db.createUser({
  user: "analyst",
  pwd: "analyst",
  roles: [
    { role: "read", db: "test2" }
  ]
});
