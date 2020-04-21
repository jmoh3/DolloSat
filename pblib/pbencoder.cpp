#include <iostream>
#include <fstream>
#include "PBParser.h"
#include "pb2cnf.h"

using namespace std;
using namespace PBLib;


int main(int argc, char **argv)
{
  if (argc != 14) {
    return 1;
  }

  PB2CNF pb2cnf;

  int32_t first_fresh_variable = atoi(argv[10]) + atoi(argv[11]);
  int saved_first_var = first_fresh_variable;
  int num_clauses = 0;

  char* filename = argv[13];

  cout << filename << endl;

  ofstream write_file;
  write_file.open(filename);

  for (int i = 1; i < argc-1; i+=3) {
    int32_t start_var = atoi(argv[i]);
    int32_t num_vars = atoi(argv[i+1]);
    int k = atoi(argv[i+2]);
    
    vector< int32_t > literals;

    for (int i = 0; i < num_vars; i++) {
      literals.push_back(i+start_var);
    }

    vector<vector<int32_t>> formula;
    first_fresh_variable = pb2cnf.encodeAtMostK(literals, k, formula, first_fresh_variable) + 1;
    first_fresh_variable = pb2cnf.encodeAtLeastK(literals, k, formula, first_fresh_variable) + 1;

    for (auto clause : formula)
    {
      for (auto lit : clause)
        write_file << lit << " ";
      write_file << "0\n";
    }
    num_clauses += formula.size();
  }
  
  int added_vars = first_fresh_variable - (saved_first_var);

  write_file << "+vars= " << added_vars << "\n";
  write_file << "+clauses= " << num_clauses;

  write_file.close();

  return 0;
}