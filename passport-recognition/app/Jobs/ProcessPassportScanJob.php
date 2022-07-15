<?php

namespace App\Jobs;

use App\Models\Passport;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldBeUnique;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;

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
    public function __construct($image_path)
    {
        $this->image_path = $image_path;


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
        $result = $process->getOutput();
        $string = str_replace(array("\n", "\r"), '', $result);
        $decoded_array = json_decode($string);
        var_dump($decoded_array);

    }
}
