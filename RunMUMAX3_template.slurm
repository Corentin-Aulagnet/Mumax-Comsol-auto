#!/bin/bash -x 

#SBATCH --account=gho35

#SBATCH --partition=gpu

#SBATCH --job-name=$JOB_NAME

#SBATCH --output=slurm-%x.%N.%j.out 
#SBATCH --error=slurm-%x.%N.%j.err 

#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user=receive.slurm.aulagnet@gmail.com

#SBATCH --nodes=1                ## number of nodes 
#SBATCH --ntasks=1               ## total number of mpi tasks
#SBATCH --ntasks-per-node=1      ## mpi tasks per node
#SBATCH --cpus-per-task=1        ## ALWAYS 1 ! ## 

#SBATCH --gres=gpu:1             ## number of GPU cards

#SBATCH --time=00:10:00

  ## the input name
  input_name=$MUMAX_SCRIPT

########################################################
## from here PROBABLY you don't need to edit anything ##
########################################################
 
  ## slurm info
  env | grep -i slurm 
 
  ## enforcing the submission directory
  cd $SLURM_SUBMIT_DIR
  echo "SUBMISSION DIRECTORY $SLURM_SUBMIT_DIR"
  
  ## creating temporary directory in $SCRATCHDIR
  WORKDIR="$SCRATCHDIR/job.$SLURM_JOB_ID.$USER"
  mkdir -p $WORKDIR

  ## checking if the WORKDIR was created
  if [ -e $WORKDIR ] ; then 

    ## cheching if exist the INPUT in the submission directory 
    finp=$SLURM_SUBMIT_DIR/$input_name
    if [ -e $finp ] ; then 
    
      cd $WORKDIR
      echo "WORKING DIRECTORY $WORKDIR"
      echo "INPUT FILE $finp"

      ## loading the module MUMAX 
      module purge
      module load mumax/3.10b
      export OMP_NUM_THREADS=1  ## ALWAYS 1 ##
      ulimit -s unlimited
      unset I_MPI_PMI_LIBRARY

      ## copying extra files
      rsync -avzr --exclude={'*slurm*','reference*z'} $SLURM_SUBMIT_DIR/* $WORKDIR

      ## printing the files copied to WORKDIR
      echo "Files in $WORKDIR"
      ls -lh *

      echo "  Started  : $(date)"
      time mumax3 $input_name >& Output.txt 2>&1
      echo "  Finished : $(date)"

      ## copying everything back to submission directory
      fout="$SLURM_SUBMIT_DIR/output_$input_name"
	  fout=${fout%.*}
      if [ ! -e $fout ]; then
        mkdir $fout
      fi
      mv $WORKDIR/* $fout

    ## if there is no input file do nothing and exit after cleaning the workdir
    else 
      echo "ERROR: INPUT $($finp) is missing"
    fi 

    ## going back to the submission directory 
    cd $SLURM_SUBMIT_DIR

    ## cleaning the scratchdir
    rm $WORKDIR/*
    rmdir $WORKDIR

  ## if the wrokdir cannot be created do nothing and exit
  else
    echo "ERROR: WORKDIR ($WORKDIR) was not created"
  fi
