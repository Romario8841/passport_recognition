<?php

namespace App\Jobs;

use App\Models\Passport;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldBeUnique;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;

use Illuminate\Support\Facades\Log;
use Mockery\Exception;
use Symfony\Component\Process\Exception\ProcessFailedException;
use Symfony\Component\Process\Process;

class ProcessPassportScanJob implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    protected $image_path;

    /**
     * Create a new job instance.
     *
     * @return void
     */
    public function __construct($image_path, $passport)
    {
        $this->image_path = $image_path;
        $this->passport   = $passport;

    }

    /**
     * Execute the job.
     *
     * @return void
     */
    public function handle()
    {

        $process = new Process(['python', "passport_recognition\server.py", $this->image_path]);
        $process->run();
        $result_error = $process->getErrorOutput();
        echo $result_error;
        $result = $process->getOutput();
        $passport = Passport::where('file_path', $this->image_path)->first();
        try {
            $passport->first_name = $result;
            $passport->on_pending = false;
            $passport->save();
        }
        catch (Exception $e){
            Log::error($e->toArray());
        }


    }
}
